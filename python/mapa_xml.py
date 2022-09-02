from lxml import etree
import os

root = etree.XML('<root><a><b/></a></root>')
root_1 = etree.XML('<a><b/></a>')

xml_str = etree.tostring(root, xml_declaration=True, encoding="UTF-8", pretty_print=True)
tree = root.getroottree()
save_path_file = "gfg.xml"

parent = root.getparent()
print(parent)
# parent.insert(parent.index(root)+1, root_1)
  
with open(save_path_file, "wb") as f:
    f.write(xml_str) 