const { useState } = React;

function App() {
    const [username, setUsername] = useState("");
    const [password, setPassword] = useState("");
    const [file, setFile] = useState(null);
    const [status, setStatus] = useState("Not Running");
    const [remainingUsers, setRemainingUsers] = useState(0);
    const [estimatedTime, setEstimatedTime] = useState("0h 0m 0s");
    const [currentUser, setCurrentUser] = useState("None");
    const [showPassword, setShowPassword] = useState(false);

    const handleFileChange = (e) => {
        setFile(e.target.files[0]);
    };

    const handleStart = () => {
        if (!username || !password || !file) {
            alert("Please fill in all fields and select a CSV file.");
            return;
        }

        const formData = new FormData();
        formData.append("username", username);
        formData.append("password", password);
        formData.append("file", file);

        fetch("/start", {
            method: "POST",
            body: formData
        })
        .then(response => response.json())
        .then(data => {
            setStatus("Running");
            // Handle additional data like remaining users, estimated time, etc.
        })
        .catch(error => {
            console.error("Error:", error);
            setStatus("Error");
        });
    };

    const handleStop = () => {
        fetch("/stop", { method: "POST" })
        .then(response => response.json())
        .then(data => {
            setStatus("Stopped");
        })
        .catch(error => {
            console.error("Error:", error);
            setStatus("Error");
        });
    };

    return (
        <div className="container">
            <label>Username:</label>
            <input type="text" value={username} onChange={(e) => setUsername(e.target.value)} />

            <label>Password:</label>
            <input type={showPassword ? "text" : "password"} value={password} onChange={(e) => setPassword(e.target.value)} />

            <div className="show-password-container">
                <input type="checkbox" checked={showPassword} onChange={() => setShowPassword(!showPassword)} />
                <label>Show Password</label>
            </div>

            <label>CSV File:</label>
            <input type="file" accept=".csv" onChange={handleFileChange} />

            <button onClick={handleStart}>Start</button>
            <button onClick={handleStop}>Stop</button>

            <p>Status: {status}</p>
            <p>Remaining Users: {remainingUsers}</p>
            <p>Estimated Time Remaining: {estimatedTime}</p>
            <p>Current User: {currentUser}</p>
        </div>
    );
}

ReactDOM.render(<App />, document.getElementById("root"));
