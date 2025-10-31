import os
from flask import Flask, render_template, jsonify
from dotenv import load_dotenv
from nobel_data import get_nobel_laureates, get_all_laureates

load_dotenv()

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')

# Nobel Prize categories
CATEGORIES = {
    'physics': 'Physics',
    'chemistry': 'Chemistry',
    'medicine': 'Physiology or Medicine',
    'literature': 'Literature',
    'peace': 'Peace',
    'economics': 'Economic Sciences'
}

@app.route('/')
def index():
    """Main page with category selector"""
    return render_template('index.html', categories=CATEGORIES)

@app.route('/table')
def table_view():
    """Table view of all Nobel Prize winners"""
    all_data = get_all_laureates()

    # Flatten data for table view
    all_laureates = []
    for category, laureates in all_data.items():
        for laureate in laureates:
            laureate_copy = laureate.copy()
            laureate_copy['category'] = CATEGORIES.get(category, category)
            laureate_copy['category_key'] = category
            # Get co-laureate names
            if laureate['shared_with']:
                co_names = []
                for co_id in laureate['shared_with']:
                    co_laureate = next((l for l in laureates if l['laureate_id'] == co_id), None)
                    if co_laureate:
                        co_names.append(co_laureate['name'])
                laureate_copy['co_laureate_names'] = ', '.join(co_names)
            else:
                laureate_copy['co_laureate_names'] = '-'
            all_laureates.append(laureate_copy)

    # Sort by year descending
    all_laureates.sort(key=lambda x: x['prize_year'], reverse=True)

    return render_template('table.html', laureates=all_laureates, categories=CATEGORIES)

@app.route('/api/laureates/<category>')
def get_laureates(category):
    """Get Nobel laureates for a specific category or all categories"""
    if category == 'all':
        # Return all laureates with their category information
        all_data = get_all_laureates()
        all_laureates = []
        for cat_key, laureates in all_data.items():
            for laureate in laureates:
                laureate_copy = laureate.copy()
                laureate_copy['category'] = cat_key
                all_laureates.append(laureate_copy)

        return jsonify({
            'category': 'All Categories',
            'laureates': all_laureates
        })

    if category not in CATEGORIES:
        return jsonify({'error': 'Category not found'}), 404

    laureates = get_nobel_laureates(category)

    return jsonify({
        'category': CATEGORIES[category],
        'laureates': laureates
    })

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(debug=True, host='0.0.0.0', port=port)
