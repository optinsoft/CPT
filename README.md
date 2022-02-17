# CPT

This script allows to forward multiple local ports to the multiple remote host:port via SSH.

## Usage

```bash
python cpt.py [-h] --local-port LOCAL_PORT --remote-ip REMOTE_IP --remote-port REMOTE_PORT [--count COUNT] --ssh-host SSH_HOST [--ssh-port SSH_PORT] --ssh-user  SSH_USER --ssh-keyfile SSH_KEYFILE
```

If argument "count" equals 1 then it works exactly as this command:

```bash
ssh -L local_port:remote_ip:remote_port ssh_user@ssh_host -i ssh_keyfile
```

If count = 2 then it is similar to run 2 parallel commands:

```bash
   ssh -L local_port:remote_ip:remote_port ssh_user@ssh_host -i ssh_keyfile
   ssh -L (local_port+1):(remote_ip+1):remote_port ssh_user@ssh_host -i ssh_keyfile
```

 etc.