---
uid: 20201230134632
title: this is the test data link
aliases: []
date: 2020-12-30 13:46:32
update: 2020-12-31 16:24:11
tags: [hashtag1, hashtag2, hashtag3]
draft: false
---

Yaml Front Matter will be added to the beginning of the file.

§§Adding Yaml Front Matter

All headings and body text will be retained, including line breaks and text decoration.

Note files in subdirectories will be moved to the Root directory (excluding image files).

The note in the Inbox will be `draft: true` in Yaml Front Matter. The default is `draft: false`.

§§Replace file name and links

The file name of all notes and images will be replaced by the UID (yyyyMMddhhmmss.md).

And the link will be replaced. Wikilink will be replaced by Markdown link. The link text will retain
the original text; if an Alias is set, the Alias will be adopted as the link text. As shown below:

[[linked_file]]
[[linked_file_with_alias | alias text]]
![[image_link.png]]

Markdown link will only replace the link to the note.

[markdown_link](markdown_link.md)

§§Moving Hashtags

§§§All hashtags to Yaml Front Matter

All headings will remain intact. Headlines are not considered hashtags.

The hashtag will be moved to Yaml Front Matter and the original hashtag will have its line removed.

#hashtag1 #hashtag2 #hashtag3