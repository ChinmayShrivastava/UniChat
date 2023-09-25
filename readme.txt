### To install chromedriver follow the link below -
[https://www.swtestacademy.com/install-chrome-driver-on-mac/]
### Run the command to download CA cert for SQL database
#### MAC `curl --create-dirs -o $HOME/.postgresql/root.crt 'https://cockroachlabs.cloud/clusters/3ab356dc-9596-46a7-b6a7-4389ae45a34c/cert'`
#### Windows `mkdir -p $env:appdata\postgresql\; Invoke-WebRequest -Uri https://cockroachlabs.cloud/clusters/3ab356dc-9596-46a7-b6a7-4389ae45a34c/cert -OutFile $env:appdata\postgresql\root.crt`
#### Linux `curl --create-dirs -o $HOME/.postgresql/root.crt 'https://cockroachlabs.cloud/clusters/3ab356dc-9596-46a7-b6a7-4389ae45a34c/cert'`