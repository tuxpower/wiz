# Usage: python tf-plan-generator.py --control_id <control_id> --terraform <terraform_executable> --regenerate
# control_id: Control ID to generate Terraform plan for (required)
# terraform_executable: Path to Terraform executable (default: terraform)
# regenerate: Regenerate Terraform plan for all tests (optional)


# you can provide control id to generate terraform plan for a specific control id or for the controls that starts with the control id
# eg: to generate for all the controls starting with FW-, input control_id as FW-
# to generate for a specific control, input control_id as FW-SC_010

# The default behavior is skip the test if the json file exists in the tests folder.
# To regenerate the test, add the flag --regenerate
# The plan files are saved in the tests folder with the same name as the test file but with .json extension

import os
import subprocess
import glob
import json
import shutil
import copy
import argparse
import traceback
import time


# add logger to write to console
import logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

consoleHandler = logging.StreamHandler()
consoleHandler.setLevel(logging.INFO)

logger.addHandler(consoleHandler)

formatter = logging.Formatter(
    '%(asctime)s  %(levelname)s: %(message)s')
consoleHandler.setFormatter(formatter)
# add logger to write to file
fileHandler = logging.FileHandler('tf-execute.log', mode='w')   

fileHandler.setFormatter(formatter)
logger.addHandler(fileHandler)

TF_EXECUTABLE = "terraform"

provider = """
terraform {
  required_providers {
    # azurerm = {
    #   source  = "hashicorp/azurerm"
    #   version = "~>3.116"
    # }
    # random = {
    #   source  = "hashicorp/random"
    #   version = "3.6.0"
    # }
    # time = {
    #   source  = "hashicorp/time"
    #   version = "~> 0.9"
    # }
    # azapi = {
    #   source  = "azure/azapi"
    #   version = "<= 1.12"
    # }
    # tls = {
    #   source  = "hashicorp/tls"
    #   version = "~>3.0"
    # }
  }
#   backend "azurerm" {{}}
}

provider "azurerm" {
    subscription_id = "74b2055f-957a-4017-b002-9ef45ef9c3e7"
  features {
    key_vault {
      recover_soft_deleted_certificates          = true
      recover_soft_deleted_secrets               = true
      recover_soft_deleted_keys                  = true
    }
  }
  storage_use_azuread        = true
  skip_provider_registration = true
  
}

"""

def load_json_file(json_file):
    """Load the test metadata from the JSON file."""
    with open(json_file,'r',encoding="utf-8") as f:
        return json.load(f)


    


def run_tf_commands(folder_path,filename, tf_executable):
    # check if running from powershell
    logger.info("Running Terraform commands with Executable %s", tf_executable)
    # Get Terraform version
    subprocess.run([tf_executable, "version"], check=True)
    # change directory folder path
    os.chdir(folder_path)

    # run terraform fmt command
    logger.info("Running terraform fmt in %s", folder_path)
    try:
        subprocess.run([tf_executable, "fmt", "-recursive"], check=True)
    except subprocess.CalledProcessError as e:
        logger.error("Error running terraform fmt in %s: %s", folder_path, e)
        raise

    # Initialize Terraform in the current directory
    logger.info("Running terraform init in %s", folder_path)
   
    try:
       
        subprocess.run([tf_executable, "init", "-input=false"], check=True)
    except subprocess.CalledProcessError as e:
        logger.error("Error running terraform init in %s: %s", folder_path, e)
        raise

    # Run Terraform plan and save the output to a plan file
    logger.info("Running terraform plan in %s", folder_path)
    # subprocess.run(["terraform", "plan", "-var-file=terraform.tfvars", "-out=out.tfplan"], check=True)
    try:
        subprocess.run([tf_executable, "plan", "-lock=false",  "-out=out.tfplan"], check=True)
    except subprocess.CalledProcessError as e:
        logger.error("Error running terraform plan in %s: %s", folder_path, e)
        raise

   

    # Output the plan to a JSON file
    logger.info("Outputting terraform plan to JSON in %s", folder_path)
    try:
        with open(f"{filename}.json", "w") as json_file:
            subprocess.run([tf_executable, "show", "-json", "out.tfplan"], stdout=json_file, check=True)
    except subprocess.CalledProcessError as e:
        logger.error("Error running terraform show in %s: %s", folder_path, e)
        raise
    # format json file
    json_data = load_json_file(f"{filename}.json")
    with open(f"{filename}.json", "w") as json_file:
        json.dump(json_data, json_file, indent=4)

# Get the directory of the script
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

logger.info("SCRIPT_DIR : %s", SCRIPT_DIR)
# Get the parent directory
# ROOT_DIR = os.path.dirname(SCRIPT_DIR)
ROOT_DIR = SCRIPT_DIR
logger.info("ROOT_DIR : %s", ROOT_DIR)
os.environ["TF_PLUGIN_CACHE_DIR"] = os.path.join(ROOT_DIR, ".terraform.d/plugin-cache")  # Set the plugin cache directory

os.environ["TF_PLUGIN_CACHE_MAY_BREAK_DEPENDENCY_LOCK_FILE "] = "true"
    # create cache directory
os.makedirs(os.environ["TF_PLUGIN_CACHE_DIR"], exist_ok=True)
# Set the parent directory where all subfolders with Terraform configurations are located
POLICY_DIR = os.path.join(ROOT_DIR, "SCF", "DigitalPolicies")
logger.info("POLICY_DIR : %s", POLICY_DIR)


def get_folder_names(control_id):
    # get the full path folder name from the POLICY_DIR that has the control_id
    folder_names = []
    # get the folder name from the POLICY_DIR that has the control_id
    for item in os.listdir(POLICY_DIR):
        item_path = os.path.join(POLICY_DIR, item)
        if os.path.isdir(item_path):
            folder_name_only = os.path.basename(item_path)
            if control_id == "all" :
                folder_names.append(item_path)    
            else:
                if folder_name_only.startswith(control_id):
                    folder_names.append(item_path)
                    continue

    
    
    return folder_names

    
def process_control(folder_path, regenerate,tf_executable=TF_EXECUTABLE):
    # get the folder name from the POLICY_DIR that has the control_id
    
    #get the folder name from the path
    folder_name = os.path.basename(os.path.normpath(folder_path))
    logger.info("foldername : %s", folder_name)
    output_dir = os.path.join(folder_path, "terraform", "tfoutput")
    
    os.makedirs(output_dir, exist_ok=True)
    dir_to_process = os.path.join(folder_path, "terraform", "tests")
    logger.info("Processing folder: %s", dir_to_process)

    # if regenerate:
    #     # delete files from dir_to_process that end with .json
    #     files = glob.glob(f"{dir_to_process}/*.json")
    #     for f in files:
    #         os.remove(f)
    metadata_file = os.path.join(dir_to_process, "test-metadata.json")
    test_metadata = load_json_file(metadata_file)  
    plan_tests = []
    # from test_metadata get entries where filename ends with .tf
    existing_tests = [test for test in test_metadata if test["filename"].endswith(".tf")]
    # print(json.dumps( existing_tests, indent=4))    
    # return
    generated_files = []
    # read generated_files.txt and store in a list
    # check if generated_files.txt exists
    # read the file and store in a list without the newline character
    plan_files = [test["filename"] for test in test_metadata if test["filename"].endswith(".json")]
    print(plan_files)
    for test in existing_tests:

        try:
            test_file = os.path.join(dir_to_process, test["filename"])      
            
            # return
            # get the filename without extension
            filename = os.path.splitext(test["filename"])[0]
            # check json file exists in dir_to_process,  skip the test if not regenerate
            if os.path.exists(os.path.join(dir_to_process, f"{filename}.json")):
                if regenerate:
                    logger.info("Regenerate flag is set. Regenerating test: %s.json", filename)
                    # remove json file  
                    os.remove(os.path.join(dir_to_process, f"{filename}.json"))
                else:
                    # if f"{filename}.json" in plan_files:
                        # logger.info("Skipping test: %s", test_file)
                        # continue
                   
                    logger.info("Adding test: %s.json to test-metadata.json", filename)
                    new_test =  copy.deepcopy(test)
                    new_test['description'] = f"{test['description']} - plan"
                    new_test['filename'] = f"{filename}.json"
                    plan_tests.append(new_test)
                    continue
                    # plan_found = False
                    # for item in plan_files:
                    #     if item["filename"] == f"{filename}.json":
                    #         print(item['filename'])
                    #         logger.info(f"Skipping test: {test_file}")
                    #         plan_found = True
                    #         break
                    # if plan_found :
                    #     logger.info(f"Skipping test: {test_file}")
                    #     continue
               
            logger.info("Processing test: %s", test_file)
            output_test_path = os.path.join(output_dir, filename)
            logger.info("output_test_path : %s", output_test_path)
            # Remove the folder if it exists
            # if os.path.exists(output_test_path):
            #     shutil.rmtree(output_test_path)
            # create folder output_test_path
            os.makedirs(output_test_path, exist_ok=True)
            
            provider_file = os.path.join(output_test_path, "provider.tf")
            # copy provider block to the test file
            with open(provider_file, 'w', encoding='utf-8') as f:
                f.write(provider)
            
            # copy the test file to the output_test_path
            shutil.copy2(test_file, output_test_path)

            # copy files from tfresources to the output_test_path
            tf_resources_dir = os.path.join(ROOT_DIR, "tfresources")
            # check if tf_resources_dir exists
            if os.path.exists(tf_resources_dir):
                # copy files from tfresources to the output_test_path
                if os.name == 'nt':
                    subprocess.run(["xcopy", tf_resources_dir, output_test_path, "/E", "/Y"], check=True)
                else:
                    subprocess.run(["cp", "-r", tf_resources_dir, output_test_path], check=True)
            
            run_tf_commands(output_test_path,filename,tf_executable)

            json_plan_file = os.path.join(output_test_path, f"{filename}.json")
            if os.path.exists(json_plan_file):
                # copy tfplan.json to the dir_to_process folder
                shutil.copy2(json_plan_file, dir_to_process)
                # copy test to new_test 
                new_test =  copy.deepcopy(test)
                new_test['description'] = f"{test['description']} - plan"
                new_test['filename'] = f"{filename}.json"
                plan_tests.append(new_test)
                if test_file not in generated_files:    
                    generated_files.append(test_file)
           
        except Exception as e:
            logger.error("Error generating plan file for test: %s", test_file)
            logger.error(traceback.print_exc())
            return
        
    if len(plan_tests) >0:
        # update the test-metadata.json file
        all_tests = existing_tests + plan_tests
        with open(metadata_file, 'w') as f:
            json.dump(all_tests, f, indent=4)
        # write generated files to the file
       
    # # remove the output folder
    # # Ensure all file operations are completed before removing the directory
    # try:
    #     #remove the output folder including all files and subdirectories
    #     # add sleep to wait for file operations to complete
    #     time.sleep(5)
    #     if os.path.exists(output_dir):
    #         shutil.rmtree(output_dir)
    # except Exception as e:
    #     logger.error(f"Error removing directory {output_dir}: {e}")
    #     raise
    # write generated files to the file 
    
    logger.info("Terraform plan generated successfully.")
    return generated_files

# add argument parser to the script
def argumentparser():
    # Create an ArgumentParser object with a description
    parser = argparse.ArgumentParser(description='Terraform Plan Generator')

    # Argument for the Control Id
    parser.add_argument(
        '--control_id',
        metavar='Control ID',
        type=str,
        default='all',
        help='Control ID to generate Terraform plan for'
    )
    # add argument that accepts terraform executable path and default to terraform
    parser.add_argument(
        '--terraform',
        metavar='Terraform Executable',
        type=str,
        default='terraform',
        help='Path to Terraform executable'
    )
    # add argument that accepts regenerate flag and default to False
    parser.add_argument(
        '--regenerate',
        action='store_true',
        help='Regenerate Terraform plan for all tests'  
    )
    # Parse the command-line arguments and return the result
    return parser.parse_args()


def main():
    try:
        args = argumentparser()
        logger.info("Arguments: %s", args)
        
        # Check if required arguments are provided
        if None is args.control_id:
            logger.error("Please provide Control ID")
            return
        if args.control_id == "all":
            logger.info("Processing all controls")
        folder_paths = get_folder_names(args.control_id)
        if len( folder_paths) <=0 :
            logger.error("No folderS found with control_id starting with: %s", args.control_id)
            return None
        # print(f"folder_paths : {folder_paths}")
        generated_files = []
        for folder_path in folder_paths:
            files_processed = process_control(folder_path, args.regenerate, args.terraform)
            
        
            
    except Exception:
        # Log any exceptions
        logger.error("Error: %s", traceback.print_exc())
        
    

    pass
# write main function to the script 
if __name__ == "__main__":
   print("Starting Terraform Plan Generator")
   main()
