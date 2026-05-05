import argparse
from pathlib import Path
import logging as log

import dash
import pandas as pd
import plotly.graph_objects as go
from dash import dcc, html
import yaml

log.basicConfig(format="%(asctime)s - %(levelname)s - %(message)s", level=log.INFO)

def load_config(config_path: str = 'config.yaml') -> dict:
	"""Load configuration from YAML file."""
	with open(config_path, 'r') as f:
		return yaml.safe_load(f)

CATEGORY_STYLES = {
	"ram": {
		"line": "#6a7bd1",
		"bg": "#eef2ff",
		"border": "#c7d2fe",
	},
	"cpu": {
		"line": "#b8782b",
		"bg": "#fff6e9",
		"border": "#f1d7ad",
	},
	"disk": {
		"line": "#2f8f76",
		"bg": "#ecfbf7",
		"border": "#b8e9dc",
	},
	"network": {
		"line": "#2b87a8",
		"bg": "#ebf8ff",
		"border": "#b6e4f4",
	},
	"other": {
		"line": "#6b7280",
		"bg": "#f7f7f8",
		"border": "#e5e7eb",
	},
}

def load_tsv(tsv_path: Path) -> tuple[pd.DataFrame, str, list[str]]:
	"""Load TSV file and return data, timestamp column name, and numeric columns."""
	df = pd.read_csv(tsv_path, sep="\t")

	if df.empty:
		raise ValueError("The TSV file is empty.")

	time_col = df.columns[0]
	df[time_col] = pd.to_datetime(df[time_col], errors="coerce")
	df = df.dropna(subset=[time_col]).sort_values(time_col)

	if df.empty:
		raise ValueError("No valid timestamps found in the first column.")

	for col in df.columns[1:]:
		df[col] = pd.to_numeric(df[col], errors="coerce")

	numeric_cols = [
		col for col in df.columns[1:] if pd.api.types.is_numeric_dtype(df[col])
	]

	if not numeric_cols:
		raise ValueError("No numeric columns found after the date column.")

	log.info(f"Loaded {len(df)} rows and {len(numeric_cols)} numeric columns from {tsv_path.name}")
	return df, time_col, numeric_cols


def classify_metric(metric_name: str) -> str:
	lower_name = metric_name.lower()
	if "ram" in lower_name or "memory" in lower_name:
		return "ram"
	if "cpu" in lower_name:
		return "cpu"
	if "disk" in lower_name or "storage" in lower_name or "io" in lower_name:
		return "disk"
	if (
		"network" in lower_name
		or "net" in lower_name
		or "rx" in lower_name
		or "tx" in lower_name
	):
		return "network"
	return "other"


def slugify(value: str) -> str:
	slug = "".join(ch.lower() if ch.isalnum() else "-" for ch in value)
	while "--" in slug:
		slug = slug.replace("--", "-")
	return slug.strip("-") or "metric"


def build_figure(
	df: pd.DataFrame,
	time_col: str,
	value_col: str,
	line_color: str,
	panel_bg: str,
) -> go.Figure:
	fig = go.Figure()
	fig.add_trace(
		go.Scatter(
			x=df[time_col],
			y=df[value_col],
			mode="lines",
			name=value_col,
			line={"width": 2, "color": line_color},
		)
	)
	fig.update_layout(
		title=value_col,
		margin={"l": 40, "r": 20, "t": 50, "b": 35},
		height=280,
		template="plotly_white",
		paper_bgcolor=panel_bg,
		plot_bgcolor=panel_bg,
		xaxis_title="Time",
		yaxis_title=value_col,
	)
	return fig


def create_app(tsv_path: Path) -> dash.Dash:
	app = dash.Dash(__name__)
	app.title = "Machine Status Dashboard"

	def serve_layout() -> html.Div:
		df, time_col, numeric_cols = load_tsv(tsv_path)
		log.info(
			f"Rendering dashboard with {len(numeric_cols)} metrics: {', '.join(numeric_cols)}"
		)

		menu_links = []
		sections = []
		for col in numeric_cols:
			category = classify_metric(col)
			style = CATEGORY_STYLES.get(category, CATEGORY_STYLES["other"])
			anchor = f"metric-{slugify(col)}"

			menu_links.append(
				html.A(
					col,
					href=f"#{anchor}",
					style={
						"textDecoration": "none",
						"padding": "8px 12px",
						"borderRadius": "999px",
						"fontSize": "14px",
						"fontWeight": "600",
						"color": "#1f2937",
						"backgroundColor": style["bg"],
						"border": f"1px solid {style['border']}",
						"display": "inline-block",
					},
				)
			)

			sections.append(
				html.Div(
					id=anchor,
					children=[
						html.H3(
							col,
							style={"margin": "0 0 8px", "color": style["line"]},
						),
						dcc.Graph(
							figure=build_figure(
								df,
								time_col,
								col,
								line_color=style["line"],
								panel_bg=style["bg"],
							),
							config={"displayModeBar": False},
						),
					],
					style={
						"marginBottom": "16px",
						"padding": "10px 12px 6px",
						"backgroundColor": style["bg"],
						"border": f"1px solid {style['border']}",
						"borderRadius": "10px",
					},
				)
			)

		return html.Div(
			children=[
				html.H2("Machine Metrics Over Time"),
				html.P(f"Source file: {tsv_path.name}"),
				html.Nav(
					children=menu_links,
					style={
						"display": "flex",
						"flexWrap": "wrap",
						"gap": "8px",
						"padding": "10px",
						"margin": "4px 0 14px",
						"position": "sticky",
						"top": "0",
						"zIndex": "50",
						"backgroundColor": "#ffffff",
						"border": "1px solid #e5e7eb",
						"borderRadius": "10px",
					},
				),
				*sections,
			],
			style={
				"maxWidth": "1200px",
				"margin": "0 auto",
				"padding": "12px 16px 32px",
				"scrollBehavior": "smooth",
				"fontFamily": "Arial, sans-serif",
			},
		)

	app.layout = serve_layout
	return app


def parse_args() -> argparse.Namespace:
	parser = argparse.ArgumentParser(description="TSV machine status dashboard")
	parser.add_argument(
		"--file",
		"-f",
		help="Path to TSV file (overrides config.yaml)",
	)
	return parser.parse_args()


def main() -> None:
	args = parse_args()
	tsv_path = Path(args.file)
	app = create_app(tsv_path)
	log.info(f"Starting dashboard server at http://{args.host}:{args.port} with data from {tsv_path}")
	app.run(host=args.host, port=args.port, debug=False)


if __name__ == "__main__":
	config = load_config()
	args = parse_args()
	
	# Use command-line argument if provided, otherwise use config
	tsv_path = Path(args.file) if args.file else Path(config['logging']['logfile'])
	host = config['dashboard']['host']
	port = config['dashboard']['port']
	
	app = create_app(tsv_path)
	log.info(f"Starting dashboard server at http://{host}:{port} with data from {tsv_path}")
	app.run(host=host, port=