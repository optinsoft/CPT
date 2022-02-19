# CPT.py

This script allows to forward multiple local ports to the multiple remote host:port via SSH.

## Usage

You can either provide command line arguments to `cpt.py`:

```bash
python cpt.py [-h] --local-port LOCAL_PORT --remote-ip REMOTE_IP --remote-port REMOTE_PORT [--count COUNT] --ssh-host SSH_HOST [--ssh-port SSH_PORT] --ssh-user SSH_USER --ssh-keyfile SSH_KEYFILE
```

or use the configuration file:

```bash
python cpt.py --config=path_to_config.json
```

If argument "count" equals 1 (default) then it works exactly as this command:

```bash
ssh -L local_port:remote_ip:remote_port ssh_user@ssh_host -i ssh_keyfile
```

If count = 2 then it is similar to run 2 parallel commands:

```bash
   ssh -L local_port:remote_ip:remote_port ssh_user@ssh_host -i ssh_keyfile
   ssh -L (local_port+1):(remote_ip+1):remote_port ssh_user@ssh_host -i ssh_keyfile
```

 etc.

## Configuration file

Example:

```json
{
    "local_port": 8102,
    "remote_ip": "10.0.0.2",
    "remote_port": 5555,
    "count": 60,
    "ssh_host": "216.58.210.174",
    "ssh_port": 22,
    "ssh_user": "user",
    "ssh_keyfile": "~/keyfile.pem"
}
```

## Commands

command | description
---- | -----------
`exit`|Stop forwardings and exit.
`help`|Display help.
`list`|List forwardings.
`adb-connect`|Run for each forwarded port `<localport>`: `adb connect 127.0.0.1:<local_port>`
`adb-disconnect`|Run for each forwarded port `<localport>`: `adb disconnect 127.0.0.1:<local_port>`
`adb-devices`|Run: `adb devices`
`adb-push`|Run for each forwarded port `<localport>`: `adb -s 127.0.0.1:<local_port> push ...`
`adb-shell`|Run for each forwarded port `<localport>`: `adb -s 127.0.0.1:<local_port> shell ...`
`adb-install`|Run for each forwarded port `<localport>`: `adb -s 127.0.0.1:<local_port> install ...`
