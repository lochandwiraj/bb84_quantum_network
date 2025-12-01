# 🔐 BB84 Quantum Key Distribution Network Simulator

A complete web-based implementation of the BB84 quantum key distribution protocol with multi-attacker scenario analysis and real-time visualizations.

## 🚀 Quick Start

### Prerequisites
- Python 3.x with pip
- Node.js with npm

### Installation

1. **Install Python Dependencies**
```bash
pip install -r requirements.txt
```

2. **Install Frontend Dependencies**
```bash
cd bb84-frontend
npm install
cd ..
```

### Running the Application

**Step 1: Start Backend API**
```bash
python api.py
```
✅ API running at http://localhost:5000

**Step 2: Start Frontend (in a new terminal)**
```bash
cd bb84-frontend
npm run dev
```
✅ Web app running at http://localhost:5173

**Step 3: Open Browser**
Navigate to **http://localhost:5173**

## 🎯 Features

### Interactive Web Interface
- **Qubit Range**: 1-20 qubits per simulation
- **Scenario Count**: 1-10 random attack scenarios
- **One-Click Execution**: Run complete analysis with single button
- **Real-Time Results**: All visualizations displayed instantly

### Visualizations
- **Network Topology Diagrams**: Visual representation of quantum network
  - Alice (sender) at center
  - Multiple receivers in circular layout
  - Attackers positioned strategically
  - Color-coded secure/compromised links
  
- **Comparison Charts**: Bar graphs comparing security across scenarios
- **Attacker Analysis**: Success rates and error induction metrics
- **Statistics Dashboard**: Overall security metrics

### Attack Scenarios
- No Attack (baseline)
- Single Attacker → Single Target
- Single Attacker → Multiple Targets
- Multiple Attackers → Single Targets
- Multiple Attackers → Multiple Targets

## 📊 How It Works

### BB84 Protocol
1. **Alice** prepares qubits in random states using random bases
2. **Bob** measures qubits using random bases
3. **Key Sifting**: Keep only bits where bases matched
4. **Error Detection**: Calculate quantum bit error rate (QBER)
5. **Security Check**: If QBER > 11%, eavesdropping detected

### Attack Detection
- **Intercept-Resend**: Eve measures and resends qubits
- **Error Introduction**: Basis mismatch causes detectable errors
- **Statistical Analysis**: Error rates reveal eavesdropping

## 🎮 Usage

### Web Interface
1. Open http://localhost:5173
2. Adjust number of qubits (1-20)
3. Set number of scenarios (1-10)
4. Click "🚀 Run Random Scenarios"
5. View all visualizations and statistics

### Command Line (Alternative)
```bash
# Single scenario with matplotlib windows
python main.py

# Multiple random scenarios
python main.py --random 5
```

## 📡 API Endpoints

### POST /api/network/random
Generate multiple random attack scenarios
```json
{
  "num_qubits": 10,
  "num_scenarios": 5
}
```

### POST /api/network/single
Single network scenario with custom parameters
```json
{
  "num_qubits": 10,
  "attack_scenario": "single_attacker_multiple_targets",
  "num_attackers": 2,
  "intercept_rate": 0.5
}
```

### POST /api/bb84/basic
Basic BB84 simulation
```json
{
  "num_qubits": 10,
  "eve_present": true,
  "intercept_rate": 0.5
}
```

### GET /api/health
Health check endpoint

## 🔧 Project Structure

```
bb84_quantum_network/
├── api.py                    # Flask REST API
├── main.py                   # CLI visualization tool
├── network.py                # Network simulation logic
├── bb84_core.py              # Core BB84 protocol
├── alice.py                  # Sender implementation
├── bob.py                    # Receiver implementation
├── eve.py                    # Attacker implementation
├── circuit.py                # Quantum circuit utilities
├── dashboard.py              # Dashboard utilities
├── error_check.py            # Error checking functions
├── correlation_analysis.py   # Correlation analysis
├── threat_analysis.py        # Threat analysis
├── requirements.txt          # Python dependencies
├── index.html                # Simple HTML interface
└── bb84-frontend/            # React application
    ├── src/
    │   ├── App.jsx           # Main app component
    │   ├── RandomScenarios.jsx  # Visualization component
    │   └── main.jsx          # Entry point
    ├── package.json          # Node dependencies
    └── vite.config.js        # Vite configuration
```

## 🎨 Technology Stack

### Backend
- Python 3.14
- Flask 3.0.0 - REST API
- Qiskit 2.2.3 - Quantum simulation
- Matplotlib 3.10.7 - Visualization generation
- NumPy 2.3.4 - Numerical computation

### Frontend
- React 19.2.0 - UI framework
- Vite 7.2.1 - Build tool
- Tailwind CSS 3.4.3 - Styling
- Framer Motion 12.23.24 - Animations

## 🎓 Educational Value

This simulator demonstrates:
- **Quantum Cryptography**: Real implementation of BB84 protocol
- **Security Analysis**: How eavesdropping is detected
- **Network Topology**: Multi-party quantum communication
- **Attack Vectors**: Various eavesdropping strategies
- **Statistical Methods**: Error rate analysis and thresholds

## 📈 Example Output

When you run 5 scenarios with 10 qubits:
- 5 different attack scenarios (randomly selected)
- 25 total links tested (5 receivers × 5 scenarios)
- Security analysis across all scenarios
- Individual network diagrams showing:
  - Alice sending to 5 receivers (Bob, Charlie, Dave, Diana, Eve_R)
  - 1-3 attackers per scenario
  - Color-coded links showing which are secure/compromised
  - Error rates on each link

## 🔒 Security Threshold

- **Safe**: QBER < 11% (link is secure)
- **Compromised**: QBER ≥ 11% (eavesdropping detected)

## 🎉 Features Highlights

✅ Full BB84 protocol implementation
✅ Multi-party quantum network simulation
✅ Multiple attack scenarios
✅ Real-time web visualizations
✅ Interactive controls
✅ Comprehensive statistics
✅ Beautiful modern UI
✅ Smooth animations
✅ Error handling
✅ Responsive design

## 📝 License

This project is for educational purposes.

## 🙏 Acknowledgments

Built with Qiskit for quantum simulation and React for the web interface.

---

**Currently Running:**
- Backend API: http://localhost:5000
- Frontend App: http://localhost:5173

Open the frontend URL and start exploring quantum key distribution! 🔐✨
