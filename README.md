# Ad Category Taxonomy Classifier

Used to give ad categories to articles which do not have ad categories.
Give classifier text to classify and response will be in json format.


## Setup Instructions
Create the google cloud instance:    
  + `terraform init` && `terraform apply`

SCP Files to Instances
  + `gcloud compute scp [file] [instance_name]:~`

Build the Docker Container:  
  + `make build`

Install CMake:  
  + `curl -L https://github.com/Kitware/CMake/releases/download/v3.15.2/cmake-3.15.2-Linux-x86_64.sh -o /opt/cmake-3.15.2-Linux-x86_64.sh`
  + `chmod +x /opt/cmake-3.15.2-Linux-x86_64.sh`
  + `yes yes | bash /opt/cmake-3.15.2-Linux-x86_64.sh`  
  + `ln -s /app/cmake-3.15.2-Linux-x86_64/bin/cmake /usr/bin`  
  + `cmake --version`  

Install XGBoost (https://xgboost.readthedocs.io/en/latest/build.html):  
  + `git clone --recursive https://github.com/dmlc/xgboost`  
  + `cd xgboost`  
  + `mkdir build`  
  + `cd build`
  + `cmake .. -DUSE_CUDA=ON`  
  + `make -j4`  

XGBoost Python Package Download:  
  + `cd python-package && python setup.py install`


## Instructions for Use
Run
  + `sudo docker exec -it "ad-category-container" python run.py`
