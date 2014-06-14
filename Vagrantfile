VAGRANTFILE_API_VERSION = "2"

Vagrant.configure(VAGRANTFILE_API_VERSION) do |config|
    config.vm.network "private_network", ip: "192.168.50.11"
    config.vm.box = "precise64"
    config.vm.box_url = "http://files.vagrantup.com/precise64.box"
    config.ssh.forward_agent = true
    config.vm.synced_folder "salt/roots/", "/srv/salt/"
    config.vm.network :forwarded_port, host: 9202, guest: 9200
    config.vm.provision :salt do |salt|
        salt.minion_config = "salt/minion"
      	salt.run_highstate = true
    end
end
