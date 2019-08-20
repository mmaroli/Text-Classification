provider "google" {

  project = "leafgroup-pbp"
  region = "us-west1"
  zone = "us-west1-b"
}


resource "google_compute_firewall" "external-ssh" {
  name = "external-ssh"
  network = "default"

  allow {
    protocol = "tcp"
    ports = ["22"]
  }
  source_ranges = ["0.0.0.0/0"]
  target_tags = ["externalssh"]
}


data "google_compute_image" "my_image" {
  family = "ubuntu-1604-lts"
  project = "ubuntu-os-cloud"
}

resource "google_compute_instance" "default" {
  name = "gpu-training"
  machine_type = "n1-highmem-4"
  zone = "us-west1-b"
  tags = ["externalssh"]

  network_interface {
    network = "default"

    access_config {
      // ssh access
    }
  }

  boot_disk {
    initialize_params {
      image = "${data.google_compute_image.my_image.self_link}"
      size = 50
    }
  }

  guest_accelerator {
    type = "nvidia-tesla-k80"
    count = 1
  }

  scheduling {
    on_host_maintenance = "TERMINATE" // Required for GPU
  }

  provisioner "remote-exec" {
    connection {
      type = "ssh"
      user = "manavmaroli"
      host = "${google_compute_instance.default.network_interface.0.access_config.0.nat_ip}"
      private_key = "${file("~/.ssh/google_compute_engine")}"
    }
    scripts = [
      "./setup/cuda.sh",
      "./setup/nvidia_docker.sh"
    ]
  }

  depends_on = ["google_compute_firewall.external-ssh"]

  metadata = {
    ssh-keys = "manavmaroli:${file("~/.ssh/id_rsa.pub")}"
  }

}
