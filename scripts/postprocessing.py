"""
Module for converting processed tree structures back to XML format.
Supports output from both Nierman-Jagadish and Wagner-Fisher algorithms.
"""

import xml.etree.ElementTree as ET
from lxml import etree

def post(arr, algorithm='nierman', output_file="myfile.xml"):
    """
    Converts processed tree array back into XML format.
    """
    xml_elements = []
    current_length = len(xml_elements)

    for node in arr:
        # Extract basic node information
        parent_tag, node_tag = node[0], node[1]
        
        if parent_tag == "0":
            root = ET.Element(node_tag)
            parent = root
            xml_elements.append(parent)
        else:
            # Find correct parent
            if node[0] == xml_elements[current_length - 1].tag:
                parent = xml_elements[current_length - 1]
            else:
                parent_index = current_length - 1
                while node[0] != xml_elements[parent_index].tag:
                    parent_index -= 1
                parent = xml_elements[parent_index]
            
            # Create element and handle algorithm-specific data
            child_element = ET.SubElement(parent, node_tag)
            if algorithm == 'wagner' and len(node) > 3:
                child_element.text = node[3]
            xml_elements.append(child_element)
            
        current_length = len(xml_elements)

    # Write to file
    tree = ET.ElementTree(root)
    tree.write(output_file, encoding="unicode", xml_declaration=True, pretty_print=True)

def print_xml_tree(root, level=0):
    """Helper function to print XML tree structure."""
    print("  " * level + root.tag)
    for child in root:
        print_xml_tree(child, level + 1)

def format_xml(input_file, output_file=None):
    """
    Formats XML file with proper indentation.
    """
    if output_file is None:
        output_file = input_file
        
    parser = etree.XMLParser(remove_blank_text=True)
    tree = etree.parse(input_file, parser)
    tree.write(output_file, pretty_print=True, encoding='unicode')

def generate_diff_report(edit_script, output_file="diff_report.txt"):
    """
    Generates a human-readable diff report from edit script.
    """
    with open(output_file, 'w') as f:
        for operation, source, target in edit_script:
            if operation == 'update':
                f.write(f"Update: {source[1]} -> {target[1]}\n")
            elif operation == 'delete':
                f.write(f"Delete: {source[1]}\n")
            elif operation == 'insert':
                f.write(f"Insert: {target[1]}\n")