# Install CUDA on Host on Ubuntu 16.04 (https://marmelab.com/blog/2018/03/21/using-nvidia-gpu-within-docker-container.html)

# Install NVIDIA Repo Metadata
sudo apt-get update
sudo apt-get install -y wget
wget https://developer.download.nvidia.com/compute/cuda/repos/ubuntu1604/x86_64/cuda-repo-ubuntu1604_9.1.85-1_amd64.deb
sudo dpkg --install cuda-repo-ubuntu1604_9.1.85-1_amd64.deb

## Install CUDA GPG Key
sudo apt install -y gnupg-curl
sudo apt-key adv --fetch-keys https://developer.download.nvidia.com/compute/cuda/repos/ubuntu1604/x86_64/7fa2af80.pub

sudo apt-get update
sudo apt install -y cuda=9.1.85-1

sudo apt-get install pciutils

echo "# CUDA" >> ~/.bashrc
echo "export PATH=/usr/local/cuda-9.1/bin:"\$PATH"" >> ~/.bashrc
echo "export LD_LIBRARY_PATH=/usr/local/cuda-9.1/lib64:"\$LD_LIBRARY_PATH"" >> ~/.bashrc

source ~/.bashrc

# NVIDIA Persistence Daemon
sudo mkdir /usr/lib/systemd/system
echo "[Unit]
Description=NVIDIA Persistence Daemon
Wants=syslog.target

[Service]
Type=forking
PIDFile=/var/run/nvidia-persistenced/nvidia-persistenced.pid
Restart=always
ExecStart=/usr/bin/nvidia-persistenced --verbose
ExecStopPost=/bin/rm -rf /var/run/nvidia-persistenced

[Install]
WantedBy=multi-user.target" | sudo tee -a /usr/lib/systemd/system/nvidia-persistenced.service

sudo systemctl enable nvidia-persistenced


# Disable some UDEV Rule
sudo sed -i 's/SUBSYSTEM=="memory".*//' /lib/udev/rules.d/40-vm-hotadd.rules
