# Axelar EVM Chain Monitoring Tool

This metrics exporter monitors which chains are registered on axelar validators. Axelar is a cross-chain communication platform that connects various blockchain ecosystems. This tool checks the status of different EVM chains maintained by a specified Axelar validator.

The primary function of this tool is to fetch and maintain a list of maintainers, known as "valopers," for a given EVM chain. The tool then serves these metrics over HTTP at the `/metrics` endpoint, which can be scraped by monitoring systems like Prometheus.

## Output Values

The tool provides a gauge metric named `evm_chain_registered`, which signifies the registration status of the monitored chains. The possible values are:

- `2` if the chain is registered
- `1` if the tool could not determine the status
- `0` if the chain is not registered

This value is tagged with two labels: `chain` (the name of the EVM chain) and `valoper` (the Axelar validator being checked).

## Requirements

- Python
- An axelar RPC endpoint

## Installation

Clone the repository and configure:

```bash
git clone https://github.com/SimplyStaking/axelar-evm-exporter.git
cd evm-chain-monitor
pip install -r requirements.txt
mv example_config.json config.json
nano config.json
python exporter.py
```

## Configuration explanation
```json
{
	"rpc": "the rpc endpoint of an axelar node (usually port 26657)",
	"host": "<ip to listen on>",
	"port": "<port to listen on (remove double quotes)>",
	"watch": "<the axelar validator to monitor>",
	"chains": ["a comma separated list of lowercase strings with chains to monitor"]
}
```

## Backlog

- monitor multiple validators at once
- monitor multiple chains at once (such as testnet and mainnet)
- request timeout
- heartbeat monitoring
