"""
Core module for tree comparison and edit script generation.
Implements both Nierman-Jagadish and Wagner-Fisher algorithms.
"""

from collections import OrderedDict
import numpy as np
import copy
import postprocessing as postproc

def wagnerFisher(stringA, stringB):
    """
    Implements Wagner-Fisher algorithm for string comparison.
    """
    wordsA = stringA.split() if isinstance(stringA, str) else []
    wordsB = stringB.split() if isinstance(stringB, str) else []
    
    M = len(wordsA)
    N = len(wordsB)
    Dist = [[0 for x in range(N+1)] for y in range(M+1)]
    
    Dist[0][0] = 0
    for i in range(1, M+1):
        Dist[i][0] = Dist[i-1][0] + len(wordsA[i-1])
    for j in range(1, N+1):
        Dist[0][j] = Dist[0][j-1] + len(wordsB[j-1])
    
    for i in range(1, M + 1):
        for j in range(1, N + 1):
            Dist[i][j] = min(
                Dist[i-1][j-1] + wfCostUpdate(wordsA[i-1], wordsB[j-1]),
                Dist[i-1][j] + len(wordsA[i-1]),
                Dist[i][j-1] + len(wordsB[j-1])
            )
    
    return Dist, Dist[M][N]

def wfCostUpdate(wordA, wordB):
    """Helper function for Wagner-Fisher string comparison."""
    if wordA == wordB:
        return 1
    else:
        return abs(len(str(wordA)) - len(str(wordB)))

def subTrees(tree, subTrees):
    """
    Extracts all subtrees from the input tree structure.
    """
    current_subtree = []
    current_level = tree[0][2]
    
    for node in tree:
        if node[2] >= current_level:
            current_subtree.append(node)
        else:
            if current_subtree:
                subTrees.append(current_subtree)
            current_subtree = [node]
            current_level = node[2]
    
    if current_subtree:
        subTrees.append(current_subtree)

def rename(trees, index, parent, prefix, dictionary):
    """
    Renames tree nodes with unique identifiers.
    """
    if index >= len(trees):
        return
        
    current_tree = trees[index]
    new_name = f"{prefix}{index}"
    
    dictionary[new_name] = {
        'parent': parent,
        'tree': current_tree,
        'children': []
    }
    
    if parent:
        dictionary[parent]['children'].append(new_name)
    
    for i in range(index + 1, len(trees)):
        if trees[i][0][2] > current_tree[0][2]:
            rename(trees, i, new_name, prefix, dictionary)
        else:
            break

def calculateCosts(dict_source, trees_target, dict_costs):
    """
    Calculates transformation costs between trees.
    """
    for key in dict_source:
        dict_costs[key] = {}
        source_tree = dict_source[key]['tree']
        
        for target_tree in trees_target:
            cost = treeDist(source_tree, target_tree)
            dict_costs[key][str(target_tree)] = cost

def treeDist(treeA, treeB):
    """
    Calculates the distance between two trees.
    """
    if not treeA or not treeB:
        return float('inf')
        
    costMatrix = np.zeros((len(treeA), len(treeB)))
    
    for i in range(len(treeA)):
        for j in range(len(treeB)):
            update_cost = nodeDist(treeA[i], treeB[j])
            delete_cost = nodeDist(treeA[i], None)
            insert_cost = nodeDist(None, treeB[j])
            
            costMatrix[i][j] = min(update_cost,
                                 delete_cost + costMatrix[i-1][j] if i > 0 else float('inf'),
                                 insert_cost + costMatrix[i][j-1] if j > 0 else float('inf'))
    
    return costMatrix[-1][-1]

def nodeDist(nodeA, nodeB):
    """
    Calculates distance between two nodes.
    """
    if nodeA is None or nodeB is None:
        return 1.0
        
    if isinstance(nodeA[1], list) or isinstance(nodeB[1], list):
        return 0.0 if nodeA[1] == nodeB[1] else 1.0
    
    return 0.0 if nodeA[1] == nodeB[1] else 1.0

def toList(dictionary):
    """
    Converts tree dictionary to list format.
    """
    result = []
    stack = [k for k, v in dictionary.items() if not v['parent']]
    
    while stack:
        current = stack.pop()
        result.append(current)
        stack.extend(reversed(dictionary[current]['children']))
    
    return result

def generateEditScript(treeA, treeB, algorithm='nierman'):
    """
    Generates edit script between two trees.
    """
    edit_script = []
    
    def compare_nodes(nodeA, nodeB):
        if nodeA[1] != nodeB[1]:
            if algorithm == 'wagner' and len(nodeA) > 3 and len(nodeB) > 3:
                dist, _ = wagnerFisher(nodeA[3], nodeB[3])
                if dist > 0:
                    edit_script.append(('update', nodeA, nodeB))
            else:
                edit_script.append(('update', nodeA, nodeB))
    
    def process_trees(dictA, dictB):
        listA = toList(dictA)
        listB = toList(dictB)
        
        for nodeA in listA:
            if nodeA not in listB:
                edit_script.append(('delete', dictA[nodeA]['tree'], None))
        
        for nodeB in listB:
            if nodeB not in listA:
                edit_script.append(('insert', None, dictB[nodeB]['tree']))
            else:
                compare_nodes(dictA[nodeA]['tree'], dictB[nodeB]['tree'])
    
    process_trees(treeA, treeB)
    return edit_script

def run(tree1, tree2, algorithm='nierman'):
    """
    Main entry point for tree comparison.
    """
    global dictA, dictB, subTreesA, subTreesB, dictCostsA, dictCostsB, ListofTreesA, ListofTreesB
    
    # Initialize structures
    dictA, dictB = {}, {}
    subTreesA, subTreesB = [], []
    
    # Process trees
    subTrees(tree1, subTreesA)
    subTrees(tree2, subTreesB)
    rename(subTreesA, 0, '', 'A', dictA)
    rename(subTreesB, 0, '', 'B', dictB)
    
    # Calculate costs
    dictCostsA, dictCostsB = {}, {}
    calculateCosts(dictA, subTreesB, dictCostsA)
    calculateCosts(dictB, subTreesA, dictCostsB)
    
    # Generate final lists
    ListofTreesA = toList(dictA)
    ListofTreesB = toList(dictB)
    
    # Generate and return edit script
    return generateEditScript(dictA, dictB, algorithm)

def patch(edit_script):
    """
    Applies edit script to generate final tree structure.
    
    Args:
        edit_script: List of edit operations (update, delete, insert)
    
    Returns:
        list: Final tree structure
    """
    final_tree = []
    
    for operation, source, target in edit_script:
        if operation == 'update':
            final_tree.append(target)
        elif operation == 'insert':
            final_tree.append(target)
        # Skip deletes as we're building the target tree
    
    return final_tree