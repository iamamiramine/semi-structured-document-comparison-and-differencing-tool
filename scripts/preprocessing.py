"""
Module for preprocessing XML documents into a format suitable for tree comparison.
Supports both Nierman-Jagadish and Wagner-Fisher algorithms.
"""

from lxml import etree

def preprocess_xml(doc, algorithm='nierman', include_attributes=True):
    """
    Preprocesses an XML document into a tree structure.
    
    Args:
        doc: Path to XML document
        algorithm: 'nierman' or 'wagner' - determines preprocessing approach
        include_attributes: Whether to include XML attributes
    
    Returns:
        list: Processed tree structure
    """
    tree = etree.parse(doc)
    root = tree.getroot()
    arr = []
    
    def process_element(element, parent_tag="0", current_depth=0):
        # Base node information
        node_info = [parent_tag, element.tag, current_depth]
        
        # Add extra information for Wagner-Fisher if needed
        if algorithm == 'wagner':
            # Add text content if available for string comparison
            node_info.append(element.text if element.text and element.text.strip() else '')
            
        arr.append(node_info)
        
        # Process attributes
        if include_attributes and element.attrib:
            for attr_name, attr_value in element.attrib.items():
                attr_node = [element.tag, [attr_name, attr_value], current_depth + 1]
                if algorithm == 'wagner':
                    attr_node.append(attr_value)
                arr.append(attr_node)
        
        # Process children
        has_children = False
        for child in element:
            has_children = True
            process_element(child, element.tag, current_depth + 1)
            
        if not has_children:
            terminal_node = [element.tag, "0", current_depth + 1]
            if algorithm == 'wagner':
                terminal_node.append('')
            arr.append(terminal_node)
    
    process_element(root)
    return arr

def print_tree(elements, algorithm='nierman'):
    """
    Pretty prints the tree structure.
    
    Args:
        elements: Processed tree structure
        algorithm: 'nierman' or 'wagner' for proper formatting
    """
    for elem in elements:
        indent = "  " * elem[2]
        base_info = f"{indent}{elem[:3]}"
        if algorithm == 'wagner' and len(elem) > 3:
            base_info += f" (text: {elem[3]})"
        print(base_info) 

def validate_xml(doc):
    """
    Validates XML document structure.
    """
    try:
        etree.parse(doc)
        return True
    except etree.XMLSyntaxError:
        return False

def get_tree_stats(elements):
    """
    Returns basic statistics about the tree structure.
    """
    max_depth = max(elem[2] for elem in elements)
    node_count = len(elements)
    leaf_nodes = sum(1 for elem in elements if elem[1] == "0")
    
    return {
        'max_depth': max_depth,
        'total_nodes': node_count,
        'leaf_nodes': leaf_nodes
    }