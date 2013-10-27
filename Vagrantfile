VAGRANTFILE_API_VERSION = "2"

Vagrant.configure(VAGRANTFILE_API_VERSION) do |config|
    config.vm.box       = 'raring64'
    config.vm.box_url   = 'http://cloud-images.ubuntu.com/vagrant/raring/current/raring-server-cloudimg-amd64-vagrant-disk1.box'

    config.vm.network :private_network, ip: '10.10.10.2'
    config.vm.synced_folder '.', '/home/vagrant/runtime'

    config.vm.provision :ansible do |ansible|
        ansible.inventory_path = 'provisioning/inventory/vagrant'
        ansible.playbook = 'provisioning/playbook.yml'    
    end

end
