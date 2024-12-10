# -*- mode: ruby -*-
# vi: set ft=ruby :
# power by Bernardo Sacuendi

# RCI, 2024. Estudante: 20211372@isptec.co.ao - Bernardo Sacuendi


Vagrant.configure("2") do |config|

    config.vm.define "server" do |server_config|
        server_config.vm.box = "ubuntu/trusty64"
        server_config.vm.hostname = "server"
        server_config.vm.network "private_network", ip: "192.168.56.2"
        server_config.vm.synced_folder "source", "/home/vagrant/source"
        server_config.vm.provider "virtualbox" do |vb|
          vb.name = "server"
          opts = ["modifyvm", :id, "--natdnshostresolver1", "on"]
          vb.customize opts
          vb.memory = "256"
        end # do vb
        server_config.vm.provision "shell", path: "bootstrap.sh"
      end 

  end # do config
  