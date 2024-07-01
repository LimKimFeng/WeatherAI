import subprocess

def install_requirements(): 
    with open('requirements.txt', 'r') as file: 
        for line in file:
            command = line.strip()
            if command: 
                print(f"Running command: {command}")
                subprocess.run(command, shell=True, check=True)

if __name__ == "__main__": 
    install_requirements()