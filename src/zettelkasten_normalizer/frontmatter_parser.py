"""
Front matter parsing utilities for YAML, TOML, and JSON formats.
"""

import json
import re
import logging
from typing import Dict, Tuple, Optional, List

# Get logger
logger = logging.getLogger(__name__)

# Try to import TOML parser
try:
    import tomllib  # Python 3.11+
except ImportError:
    try:
        import tomli as tomllib  # Fallback for older Python versions
    except ImportError:
        tomllib = None


class FrontMatterParser:
    """Parser for different front matter formats."""
    
    def __init__(self, format_type: str = "yaml"):
        """Initialize parser with specified format."""
        self.format_type = format_type.lower()
        if self.format_type not in ["yaml", "toml", "json"]:
            raise ValueError(f"Unsupported format: {format_type}")
        
        if self.format_type == "toml" and tomllib is None:
            logger.warning("TOML parser not available. Install 'tomli' package for Python < 3.11")
            raise ImportError("TOML parser not available")
    
    def detect_format(self, content: str) -> Optional[str]:
        """Detect front matter format from content."""
        lines = content.split('\n')
        if not lines:
            return None
        
        first_line = lines[0].strip()
        
        # YAML format
        if first_line == "---":
            return "yaml"
        
        # TOML format
        if first_line == "+++":
            return "toml"
        
        # JSON format
        if first_line == "{":
            return "json"
        
        return None
    
    def parse_frontmatter(self, content: str) -> Tuple[Optional[Dict], str]:
        """Parse front matter from content and return metadata and remaining content."""
        detected_format = self.detect_format(content)
        if not detected_format:
            return None, content
        
        if detected_format == "yaml":
            return self._parse_yaml(content)
        elif detected_format == "toml":
            return self._parse_toml(content)
        elif detected_format == "json":
            return self._parse_json(content)
        
        return None, content
    
    def _parse_yaml(self, content: str) -> Tuple[Optional[Dict], str]:
        """Parse YAML front matter."""
        lines = content.split('\n')
        if not lines or lines[0].strip() != "---":
            return None, content
        
        # Find the closing ---
        end_index = -1
        for i, line in enumerate(lines[1:], 1):
            if line.strip() == "---":
                end_index = i
                break
        
        if end_index == -1:
            return None, content
        
        # Extract YAML content
        yaml_lines = lines[1:end_index]
        yaml_content = '\n'.join(yaml_lines)
        
        # Simple YAML parser (basic key: value pairs)
        metadata = {}
        for line in yaml_lines:
            line = line.strip()
            if ':' in line and not line.startswith('#'):
                key, value = line.split(':', 1)
                key = key.strip()
                value = value.strip()
                # Remove quotes if present
                if value.startswith('"') and value.endswith('"'):
                    value = value[1:-1]
                elif value.startswith("'") and value.endswith("'"):
                    value = value[1:-1]
                metadata[key] = value
        
        # Return remaining content
        remaining_content = '\n'.join(lines[end_index + 1:])
        return metadata, remaining_content
    
    def _parse_toml(self, content: str) -> Tuple[Optional[Dict], str]:
        """Parse TOML front matter."""
        if tomllib is None:
            logger.error("TOML parser not available")
            return None, content
        
        lines = content.split('\n')
        if not lines or lines[0].strip() != "+++":
            return None, content
        
        # Find the closing +++
        end_index = -1
        for i, line in enumerate(lines[1:], 1):
            if line.strip() == "+++":
                end_index = i
                break
        
        if end_index == -1:
            return None, content
        
        # Extract TOML content
        toml_lines = lines[1:end_index]
        toml_content = '\n'.join(toml_lines)
        
        try:
            metadata = tomllib.loads(toml_content)
        except Exception as e:
            logger.error(f"Failed to parse TOML: {e}")
            return None, content
        
        # Return remaining content
        remaining_content = '\n'.join(lines[end_index + 1:])
        return metadata, remaining_content
    
    def _parse_json(self, content: str) -> Tuple[Optional[Dict], str]:
        """Parse JSON front matter."""
        lines = content.split('\n')
        if not lines or not lines[0].strip().startswith('{'):
            return None, content
        
        # Find the closing }
        brace_count = 0
        end_index = -1
        json_lines = []
        
        for i, line in enumerate(lines):
            json_lines.append(line)
            for char in line:
                if char == '{':
                    brace_count += 1
                elif char == '}':
                    brace_count -= 1
                    if brace_count == 0:
                        end_index = i
                        break
            if end_index != -1:
                break
        
        if end_index == -1:
            return None, content
        
        # Extract JSON content
        json_content = '\n'.join(json_lines)
        
        try:
            metadata = json.loads(json_content)
        except Exception as e:
            logger.error(f"Failed to parse JSON: {e}")
            return None, content
        
        # Return remaining content
        remaining_content = '\n'.join(lines[end_index + 1:])
        return metadata, remaining_content
    
    def serialize_frontmatter(self, metadata: Dict, content: str) -> str:
        """Serialize metadata and content into the specified format."""
        if self.format_type == "yaml":
            return self._serialize_yaml(metadata, content)
        elif self.format_type == "toml":
            return self._serialize_toml(metadata, content)
        elif self.format_type == "json":
            return self._serialize_json(metadata, content)
        
        return content
    
    def _serialize_yaml(self, metadata: Dict, content: str) -> str:
        """Serialize to YAML format."""
        yaml_lines = ["---"]
        for key, value in metadata.items():
            if isinstance(value, str) and (value.startswith('[') or ' ' in value):
                yaml_lines.append(f"{key}: {value}")
            else:
                yaml_lines.append(f"{key}: {value}")
        yaml_lines.append("---")
        yaml_lines.append("")  # Empty line after front matter
        
        return '\n'.join(yaml_lines) + content
    
    def _serialize_toml(self, metadata: Dict, content: str) -> str:
        """Serialize to TOML format."""
        toml_lines = ["+++"]
        for key, value in metadata.items():
            if isinstance(value, str):
                # Handle arrays and strings
                if value.startswith('[') and value.endswith(']'):
                    toml_lines.append(f"{key} = {value}")
                elif value in ['true', 'false']:
                    toml_lines.append(f"{key} = {value}")
                else:
                    toml_lines.append(f'{key} = "{value}"')
            else:
                toml_lines.append(f"{key} = {json.dumps(value)}")
        toml_lines.append("+++")
        toml_lines.append("")  # Empty line after front matter
        
        return '\n'.join(toml_lines) + content
    
    def _serialize_json(self, metadata: Dict, content: str) -> str:
        """Serialize to JSON format."""
        # Convert string representations of arrays/booleans to proper types
        converted_metadata = {}
        for key, value in metadata.items():
            if isinstance(value, str):
                if value.startswith('[') and value.endswith(']'):
                    try:
                        converted_metadata[key] = json.loads(value)
                    except:
                        converted_metadata[key] = value
                elif value == 'true':
                    converted_metadata[key] = True
                elif value == 'false':
                    converted_metadata[key] = False
                else:
                    converted_metadata[key] = value
            else:
                converted_metadata[key] = value
        
        json_str = json.dumps(converted_metadata, indent=2, ensure_ascii=False)
        return json_str + "\n\n" + content


def get_frontmatter_delimiters(format_type: str) -> Tuple[str, str]:
    """Get front matter delimiters for specified format."""
    if format_type == "yaml":
        return "---", "---"
    elif format_type == "toml":
        return "+++", "+++"
    elif format_type == "json":
        return "{", "}"
    else:
        raise ValueError(f"Unsupported format: {format_type}")