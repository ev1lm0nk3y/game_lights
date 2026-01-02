# Systemd Service Setup

1.  **Modify Paths**: Edit `game-lights.service` to match your installation paths.
    *   `WorkingDirectory`: Where `config.json` is located.
    *   `ExecStart`: Path to the `uv` executable or python executable.

2.  **Copy Service File**:
    ```bash
    sudo cp game-lights.service /etc/systemd/system/
    ```

3.  **Reload Daemon**:
    ```bash
    sudo systemctl daemon-reload
    ```

4.  **Enable and Start**:
    ```bash
    sudo systemctl enable game-lights
    sudo systemctl start game-lights
    ```

5.  **Check Status**:
    ```bash
    sudo systemctl status game-lights
    ```
