from flask import Flask, render_template, request, jsonify
import json
import os
from datetime import datetime

app = Flask(__name__)

# Файлы для хранения данных
STICKERS_FILE = 'stickers.json'
POSITIONS_FILE = 'positions.json'

# Загружаем существующие стикеры или создаем пустой список
def load_stickers():
    if os.path.exists(STICKERS_FILE):
        with open(STICKERS_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return []

# Сохраняем стикеры в файл
def save_stickers(stickers):
    with open(STICKERS_FILE, 'w', encoding='utf-8') as f:
        json.dump(stickers, f, ensure_ascii=False, indent=4)

# Загружаем позиции стикеров
def load_positions():
    if os.path.exists(POSITIONS_FILE):
        with open(POSITIONS_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {}

# Сохраняем позиции стикеров
def save_positions(positions):
    with open(POSITIONS_FILE, 'w', encoding='utf-8') as f:
        json.dump(positions, f, ensure_ascii=False, indent=4)

# Главная страница (для планшетов)
@app.route('/', methods=['GET', 'POST'])
def tablet_interface():
    if request.method == 'POST':
        text = request.form.get('text', '').strip()
        color = request.form.get('color', '#ffff88')
        color_number = request.form.get('color_number', '1')
        if text:
            stickers = load_stickers()
            new_id = len(stickers) + 1
            
            # Сохраняем текст с переносами строк
            formatted_text = text.replace('\n', '<br>')
            
            stickers.append({
                'text': formatted_text,  # Сохраняем с HTML переносами
                'raw_text': text,        # Сохраняем оригинальный текст
                'color': color,
                'color_number': color_number,
                'timestamp': datetime.now().strftime('%H:%M'),
                'id': new_id
            })
            save_stickers(stickers)
            return jsonify({'status': 'success'})
        return jsonify({'status': 'error', 'message': 'Текст не может быть пустым'})
    return render_template('tablet.html')

# Интерфейс тренера
@app.route('/trainer')
def trainer_interface():
    return render_template('trainer.html')

# API для получения стикеров
@app.route('/api/stickers')
def get_stickers():
    stickers = load_stickers()
    positions = load_positions()
    
    # Добавляем позиции к стикерам
    for sticker in stickers:
        sticker_id = str(sticker['id'])
        if sticker_id in positions:
            sticker.update(positions[sticker_id])
    
    return jsonify(stickers)

# API для сохранения позиции стикера
@app.route('/api/save_position', methods=['POST'])
def save_position():
    try:
        data = request.json
        sticker_id = str(data['id'])
        positions = load_positions()
        
        positions[sticker_id] = {
            'x': data.get('x', '0px'),
            'y': data.get('y', '0px'),
            'width': data.get('width', '200px'),
            'height': data.get('height', 'auto'),
            'scale': data.get('scale', 1)
        }
        
        save_positions(positions)
        return jsonify({'status': 'success'})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)})

# API для очистки стикеров
@app.route('/api/clear', methods=['POST'])
def clear_stickers():
    save_stickers([])
    save_positions({})
    return jsonify({'status': 'success'})

# API для удаления стикера
@app.route('/api/delete/<int:sticker_id>', methods=['DELETE'])
def delete_sticker(sticker_id):
    stickers = load_stickers()
    stickers = [s for s in stickers if s['id'] != sticker_id]
    save_stickers(stickers)
    
    # Удаляем позицию
    positions = load_positions()
    sticker_id_str = str(sticker_id)
    if sticker_id_str in positions:
        del positions[sticker_id_str]
        save_positions(positions)
    
    return jsonify({'status': 'success'})

# API для сохранения стикеров
@app.route('/api/save', methods=['POST'])
def save_to_file():
    stickers = load_stickers()
    filename = f"stickers_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(stickers, f, ensure_ascii=False, indent=4)
    return jsonify({'status': 'success', 'filename': filename})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)