<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Secure Web-Based Surveillance Access System</title>
    <style>
        body { margin: 0; font-family: 'Segoe UI', sans-serif; background-color: #0d0d0d; color: #e0e0e0; }
        .navbar { display: flex; justify-content: space-between; align-items: center; background: #161616; padding: 12px 25px; border-bottom: 2px solid #222; }
        .logout-btn { background: #d90429; color: white; text-decoration: none; padding: 8px 18px; border-radius: 4px; font-weight: bold; }
        .tab-container { width: 95%; max-width: 1300px; margin: 25px auto; }
        .tabs { display: flex; gap: 15px; border-bottom: 2px solid #222; margin-bottom: 25px; }
        .tab-link { background: none; color: #555; border: none; padding: 15px 25px; font-size: 15px; font-weight: bold; cursor: pointer; transition: 0.2s; }
        .tab-link.active { color: #3a86ff; border-bottom: 3px solid #3a86ff; }
        .tab-content { display: none; background: #161616; padding: 25px; border-radius: 8px; border: 1px solid #222; }
        .camera-layout { display: grid; grid-template-columns: 3fr 1fr; gap: 25px; }
        .video-box { background: #000; height: 480px; display: flex; flex-direction: column; justify-content: center; align-items: center; border: 1px solid #333; }
        .pulse { width: 12px; height: 12px; background: #ffc107; border-radius: 50%; margin-bottom: 15px; animation: pulse-animation 2s infinite; }
        @keyframes pulse-animation {
            0% { transform: scale(0.95); box-shadow: 0 0 0 0 rgba(255, 193, 7, 0.7); }
            70% { transform: scale(1); box-shadow: 0 0 0 10px rgba(255, 193, 7, 0); }
            100% { transform: scale(0.95); box-shadow: 0 0 0 0 rgba(255, 193, 7, 0); }
        }
        .sidebar { background: #222; padding: 20px; border-radius: 6px; border: 1px solid #333; }
        #log-display { background: #050505; color: #00ff41; padding: 20px; height: 400px; overflow-y: auto; font-family: 'Courier New', monospace; font-size: 14px; border: 1px solid #222; white-space: pre-wrap; line-height: 1.8; }
    </style>
</head>
<body>
    <nav class="navbar">
        <h2 style="color: #3a86ff; margin: 0; letter-spacing: 1px;">Secure Web-Based Surveillance Access System</h2>
        <a href="/logout" class="logout-btn">LOGOUT</a>
    </nav>
    <div class="tab-container">
        <div class="tabs">
            <button class="tab-link active" onclick="openTab(event, 'Camera')">VIDEO FEED</button>
            <button class="tab-link" onclick="openTab(event, 'Logs')">AUDIT LOGS</button>
        </div>
        <div id="Camera" class="tab-content" style="display: block;">
            <div class="camera-layout">
                <div>
                    <h3 style="margin-top: 0;">Node: Hardware Search Active</h3>
                    <div class="video-box">
                        <div class="pulse"></div>
                        <p style="letter-spacing: 2px; font-size: 13px; color: #666;">SEARCHING FOR 192.168.1.10</p>
                    </div>
                </div>
                <div class="sidebar">
                    <h4>Network Intel</h4>
                    <p>Status: <span style="color:#00ff41">READY</span></p>
                    <p>User: <span style="color:#3a86ff">admin</span></p>
                    <hr style="border: 0; border-top: 1px solid #444; margin: 15px 0;">
                    <p style="font-size: 12px; color: #aaa;">Database: PostgreSQL (Cloud)</p>
                    <p style="font-size: 12px; color: #aaa;">Scanning RJ45 Port 1...</p>
                </div>
            </div>
        </div>
        <div id="Logs" class="tab-content">
            <h3 style="margin-top: 0;">User Activity & Access History</h3>
            <div id="log-display">Fetching latest security events...</div>
        </div>
    </div>
    <script>
        function openTab(evt, tabName) {
            var i, tabcontent, tablinks;
            tabcontent = document.getElementsByClassName("tab-content");
            for (i = 0; i < tabcontent.length; i++) { tabcontent[i].style.display = "none"; }
            tablinks = document.getElementsByClassName("tab-link");
            for (i = 0; i < tablinks.length; i++) { tablinks[i].className = tablinks[i].className.replace(" active", ""); }
            document.getElementById(tabName).style.display = "block";
            evt.currentTarget.className += " active";
            if (tabName === 'Logs') { updateLogs(); }
        }
        function updateLogs() {
            fetch('/get_logs').then(res => res.text()).then(data => {
                const display = document.getElementById('log-display');
                display.textContent = data;
                display.scrollTop = display.scrollHeight;
            });
        }
        setInterval(() => { if(document.getElementById('Logs').style.display === 'block') updateLogs(); }, 3000);
    </script>
</body>
</html>
