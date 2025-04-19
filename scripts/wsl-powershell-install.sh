# Install system components
sudo apt update && sudo apt install -y curl gnupg apt-transport-https wget

# Download the Microsoft Repository package
wget https://packages.microsoft.com/config/debian/12/packages-microsoft-prod.deb -O packages-microsoft-prod.deb

# Install the Microsoft Repository package
sudo dpkg -i packages-microsoft-prod.deb

# Remove the Microsoft Repository package
rm packages-microsoft-prod.deb

# Update APT (optional)
sudo apt update

# Download the powershell '.tar.gz' archive
curl -L -o /tmp/powershell.tar.gz https://github.com/PowerShell/PowerShell/releases/download/v7.3.8/powershell-7.3.8-linux-arm64.tar.gz

# Create the target folder where powershell will be placed
sudo mkdir -p /opt/microsoft/powershell/7

# Expand powershell to the target folder
sudo tar zxf /tmp/powershell.tar.gz -C /opt/microsoft/powershell/7

# Set execute permissions
sudo chmod +x /opt/microsoft/powershell/7/pwsh

# Create the symbolic link that points to pwsh
sudo ln -s /opt/microsoft/powershell/7/pwsh /usr/bin/pwsh
