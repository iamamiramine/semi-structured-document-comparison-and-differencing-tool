"""
Main script for running XML tree comparison pipeline.
Supports both single comparison and dataset comparison modes.
"""

import argparse
import os
import time
import json
from pathlib import Path
import preprocessing as preproc
import processing as proc
import postprocessing as postproc

def compare_documents(doc1_path, doc2_path, algorithm, output_dir):
    """
    Compares two XML documents and generates output.
    """
    # Validate input documents
    if not all(preproc.validate_xml(doc) for doc in [doc1_path, doc2_path]):
        raise ValueError("Invalid XML document(s)")

    # Create output subdirectories
    analysis_dir = os.path.join(output_dir, 'analysis')
    documents_dir = os.path.join(output_dir, 'documents')
    os.makedirs(analysis_dir, exist_ok=True)
    os.makedirs(documents_dir, exist_ok=True)

    # Preprocess both documents
    tree1 = preproc.preprocess_xml(doc1_path, algorithm=algorithm)
    tree2 = preproc.preprocess_xml(doc2_path, algorithm=algorithm)
    
    # Get tree statistics
    stats1 = preproc.get_tree_stats(tree1)
    stats2 = preproc.get_tree_stats(tree2)
    
    # Process and get edit script
    start_time = time.time()
    edit_script = proc.run(tree1, tree2, algorithm=algorithm)
    process_time = time.time() - start_time
    
    # Generate output document
    doc1_name = os.path.basename(doc1_path)
    doc2_name = os.path.basename(doc2_path)
    output_name = f"output_{doc1_name}_{doc2_name}"
    output_path = os.path.join(documents_dir, output_name)
    
    # Generate final tree and save
    final_tree = proc.patch(edit_script)
    postproc.post(final_tree, algorithm=algorithm, output_file=output_path)
    
    # Generate diff report
    diff_path = os.path.join(analysis_dir, f"diff_{doc1_name}_{doc2_name}.txt")
    postproc.generate_diff_report(edit_script, diff_path)
    
    # Return metrics
    return {
        "document1": doc1_path,
        "document2": doc2_path,
        "algorithm": algorithm,
        "tree1_stats": stats1,
        "tree2_stats": stats2,
        "processing_time": process_time,
        "edit_script_size": len(edit_script),
        "output_document": output_path,
        "diff_report": diff_path
    }

def compare_with_dataset(input_doc, dataset_dir, algorithm, output_dir):
    """
    Compares one document against all documents in a dataset.
    """
    results = []
    
    # Get all XML files in dataset
    dataset_files = [f for f in os.listdir(dataset_dir) if f.endswith('.xml')]
    
    for dataset_file in dataset_files:
        dataset_file_path = os.path.join(dataset_dir, dataset_file)
        if dataset_file_path != input_doc:  # Avoid self-comparison
            try:
                result = compare_documents(input_doc, dataset_file_path, algorithm, output_dir)
                results.append(result)
            except Exception as e:
                print(f"Error processing {dataset_file}: {str(e)}")
    
    # Sort results by edit script size
    results.sort(key=lambda x: x['edit_script_size'])
    return results

def main():
    parser = argparse.ArgumentParser(description='XML Tree Comparison Pipeline')
    
    # Required arguments
    parser.add_argument('--mode', choices=['single', 'dataset'], required=True,
                      help='Comparison mode: single for two documents, dataset for one-to-many')
    
    parser.add_argument('--algorithm', choices=['nierman', 'wagner'], required=True,
                      help='Choice of comparison algorithm')
    
    parser.add_argument('--output', required=True,
                      help='Output directory for results')
    
    # Mode-specific arguments
    parser.add_argument('--input1', help='First input document path')
    parser.add_argument('--input2', help='Second input document path (for single mode)')
    parser.add_argument('--dataset', help='Dataset directory path')
    
    args = parser.parse_args()
    
    # Validate arguments
    if args.mode == 'single' and not (args.input1 and args.input2):
        parser.error("Single mode requires both --input1 and --input2")
    elif args.mode == 'dataset' and not (args.input1 and args.dataset):
        parser.error("Dataset mode requires both --input1 and --dataset")
    
    # Create output directory structure
    os.makedirs(args.output, exist_ok=True)
    
    try:
        # Run appropriate comparison mode
        if args.mode == 'single':
            results = [compare_documents(args.input1, args.input2, args.algorithm, args.output)]
        else:  # dataset mode
            results = compare_with_dataset(args.input1, args.dataset, args.algorithm, args.output)
        
        # Write metrics to JSON file
        metrics_file = os.path.join(args.output, 'analysis', 'comparison_metrics.json')
        with open(metrics_file, 'w') as f:
            json.dump(results, f, indent=2)
        
        # Print summary
        print("\nComparison Summary:")
        print(f"Algorithm used: {args.algorithm}")
        print(f"Number of comparisons: {len(results)}")
        print(f"\nResults saved to: {args.output}")
        print(f"Metrics saved to: {metrics_file}")
        
        # Print detailed results
        for result in results:
            print(f"\nComparison: {os.path.basename(result['document1'])} vs {os.path.basename(result['document2'])}")
            print(f"Edit script size: {result['edit_script_size']}")
            print(f"Processing time: {result['processing_time']:.2f} seconds")
            print(f"Output document: {result['output_document']}")
            print(f"Diff report: {result['diff_report']}")
            
    except Exception as e:
        print(f"Error: {str(e)}")
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main()) 