# DockerWebTerminal

**DockerWebTerminal** is a web-based terminal application built using Python's Flask-Sockets and Vue.js. This application provides a terminal interface accessible via a web browser, ideal for managing servers or running command-line tasks remotely.

![DockerWebTerminal](https://github.com/vasukushwah/flask-vue-term/blob/master/dist/static/images/image.gif?raw=true)

## Installation

### Auto Setup

To quickly set up DockerWebTerminal with automatic configuration, follow these steps:

1. **Clone the Repository:**

   ```bash
   git clone https://github.com/shreerambhakthhu/dockerwebterminalflask.git
   ```

2. **Navigate to the Script Directory:**

   ```bash
   cd dockerwebterminalflask/script
   ```

3. **Run the Installation Script:**

   ```bash
   bash installscript
   ```

   This script will install the necessary dependencies, including Nginx, and configure Flask-Vue-Term.

4. **Access the Application:**

   Once the installation is complete, navigate to your domain name or IP address in your web browser to access DockerWebTerminal.

### Manual Installation

If you prefer to set up DockerWebTerminal manually, follow these instructions:

1. **Install Python Dependencies:**

   ```bash
   pip3 install -r requirements.txt
   ```

2. **Run the Application:**

   ```bash
   python3 main.py
   ```

   The application will start and be accessible at `http://localhost:5000` in your browser.

3. **Customize Port and Host (Optional):**

   To run the server on a different port or host address, use the following command:

   ```bash
   python3 main.py --host 0.0.0.0 --port 8000
   ```

   This will start the server on port `8000` and make it accessible from any IP address.

## Usage

After installation, open your web browser and navigate to the specified address. You will be presented with a web-based terminal interface where you can execute commands just like you would in a traditional terminal.

## Contributing

Feel free to contribute to the project by submitting issues or pull requests. We welcome improvements and feedback.

## License

This project is licensed under the [MIT License](LICENSE).

For more details or support, please refer to the [GitHub Issues](https://github.com/shreerambhakthhu/dockerwebterminalflask/issues) page.
