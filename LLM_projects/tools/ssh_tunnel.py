import paramiko
import getpass

class SSHConnection:
    def __init__(self, hostname, username, password=None):
        self.hostname = hostname
        self.username = username
        self.password = password
        self.ssh_client = None

    def connect(self):
        """Establish an SSH connection to the remote server."""
        try:
            self.ssh_client = paramiko.SSHClient()
            self.ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            self.ssh_client.connect(self.hostname, username=self.username, password=self.password)
            print(f"Connected to {self.hostname}")
        except Exception as e:
            print(f"Failed to connect to {self.hostname}: {e}")

    def execute_command(self, command):
        """Executes a command on the remote server and returns the output."""
        if not self.ssh_client:
            print("SSH client is not connected.")
            return None
        try:
            stdin, stdout, stderr = self.ssh_client.exec_command(command)
            output = stdout.read().decode()
            error = stderr.read().decode()
            if error:
                print(f"Error: {error}")
            return output
        except Exception as e:
            print(f"Error running command: {e}")
            return None


    def close(self):
        """Close the SSH connection."""
        if self.ssh_client:
            self.ssh_client.close()
            print("SSH connection closed.")

# Usage in a Jupyter Notebook:
if __name__ == "__main__":
    # Provide your SSH credentials
    HOSTNAME = "lambda2.uncw.edu"  # Replace with your remote host
    USERNAME = "cld1465"            # Replace with your SSH username
    PASSWORD = getpass.getpass("Enter your password: ")

    # Create an instance of SSHConnection and connect
    ssh_conn = SSHConnection(HOSTNAME, USERNAME, PASSWORD)
    ssh_conn.connect()

    # You can now run commands on the remote server, for example:
    output = ssh_conn.execute_command("nvidia-smi")
    print(output)

    # After you're done, you can close the connection
    ssh_conn.close()
