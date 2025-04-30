.PHONY: build release format
build:
	@echo "📂 Creating output directory..."
	@mkdir -p res/generated
	@echo "📝 Generating notes.csv from words.json..."
	@uv run src/build_words.py --input res/words.json --output build/notes.csv
	@echo "🎨 Generating CSS from style.scss..."
	@sass --no-source-map src/note_models/style.scss build/style.css
	@echo "🧠 Running brainbrew..."
	@uv run brainbrew run recipes/source_to_anki.yaml
	@echo "✅ Build completed."

release: build
	@echo "📦 Packaging build deck..."
	@mkdir -p build
	@zip -r build/Ultimate_Chinese.zip build/Ultimate_Chinese
	@echo "✅ Release completed."

format:
	@uv run ruff format
	@uv run src/format_json.py --file res/words.json