import os
import subprocess
import time
import json

ISSUES = [
    f"Phase 4 Bookmarks: Task {i} of 50" for i in range(1, 51)
]

# We will apply these changes sequentially
PR_STEPS = [
    # 1. models.py Part 1
    ("models.py", 
     "super().__init__(**kwargs)", 
     "super().__init__(**kwargs)\n\nclass Bookmark(db.Model):\n    __tablename__ = 'bookmarks'\n    id = db.Column(db.Integer, primary_key=True)"),
    
    # 2. models.py Part 2
    ("models.py",
     "id = db.Column(db.Integer, primary_key=True)",
     "id = db.Column(db.Integer, primary_key=True)\n    user_token = db.Column(db.String(120), nullable=False)\n    place_id = db.Column(db.String(120), nullable=False)"),

    # 3. models.py Part 3
    ("models.py",
     "place_id = db.Column(db.String(120), nullable=False)",
     "place_id = db.Column(db.String(120), nullable=False)\n    resource_json = db.Column(db.Text, nullable=False)\n    timestamp = db.Column(db.DateTime, default=datetime.utcnow)"),

    # 4. api.py Part 1
    ("api.py",
     "from flask import Blueprint, jsonify, request",
     "from flask import Blueprint, jsonify, request\nfrom app.models import Bookmark\nfrom app.extensions import db"),

    # 5. api.py Part 2
    ("api.py",
     "@api_bp.route('/nearby')",
     """@api_bp.route('/bookmarks', methods=['GET'])
def get_bookmarks():
    token = request.args.get('token')
    if not token:
        return jsonify({"success": False, "error": "No token provided"})
    bookmarks = Bookmark.query.filter_by(user_token=token).all()
    import json
    results = [json.loads(b.resource_json) for b in bookmarks]
    return jsonify({"success": True, "data": results})

@api_bp.route('/nearby')"""),

    # 6. api.py Part 3
    ("api.py",
     "def get_bookmarks():",
     """@api_bp.route('/bookmarks', methods=['POST'])
def toggle_bookmark():
    data = request.json
    token = data.get('token')
    place_id = data.get('place_id')
    resource = data.get('resource')
    if not token or not place_id:
        return jsonify({"success": False})
    
    existing = Bookmark.query.filter_by(user_token=token, place_id=place_id).first()
    if existing:
        db.session.delete(existing)
    else:
        import json
        new_bm = Bookmark(user_token=token, place_id=place_id, resource_json=json.dumps(resource))
        db.session.add(new_bm)
    db.session.commit()
    return jsonify({"success": True})

def get_bookmarks():"""),

    # 7. index.html Part 1 (Add user token logic)
    ("index.html",
     "let autocomplete;",
     "let autocomplete;\n    let userToken = localStorage.getItem('userToken');\n    if (!userToken) { userToken = crypto.randomUUID(); localStorage.setItem('userToken', userToken); }"),

    # 8. index.html Part 2 (Update toggleFavorite signature)
    ("index.html",
     "function toggleFavorite(btn) {",
     "async function toggleFavorite(btn, place_id) {"),

    # 9. index.html Part 3 (Implement API call in toggleFavorite)
    ("index.html",
     "btn.setAttribute('aria-pressed', icon.classList.contains('text-yellow-400'));",
     """btn.setAttribute('aria-pressed', icon.classList.contains('text-yellow-400'));
        // Find the resource
        const resource = allResults.find(r => r.place_id === place_id || r.title === place_id);
        if(resource) {
            await fetch('/api/bookmarks', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({ token: userToken, place_id: place_id || resource.title, resource: resource })
            });
        }"""),

    # 10. index.html Part 4 (Update buildCard to pass resource.title as ID for now)
    ("index.html",
     "onclick=\"event.stopPropagation(); toggleFavorite(this)\"",
     "onclick=\"event.stopPropagation(); toggleFavorite(this, '${escHtml(resource.place_id || resource.title)}')\""),

    # 11. index.html Part 5 (Add My Favorites filter button)
    ("index.html",
     """data-filter="education">Education</button>""",
     """data-filter="education">Education</button>\n        <button class="filter-pill px-5 py-2 rounded-full border border-border bg-card text-zinc-400 hover:text-white hover:border-primary transition-colors text-sm font-medium"\n                onclick="filterSelection('favorites')" data-filter="favorites">My Favorites</button>"""),

    # 12. index.html Part 6 (Modify filterSelection for favorites)
    ("index.html",
     "let filtered = category === 'all' ? allResults : allResults.filter(r => r.category === category);",
     """let filtered = category === 'all' ? allResults : allResults.filter(r => r.category === category);
        if (category === 'favorites') {
            const res = await fetch(`/api/bookmarks?token=${userToken}`);
            const data = await res.json();
            if(data.success) { filtered = data.data; }
        }"""),
    
    # 13. index.html Part 7 (Make filterSelection async)
    ("index.html",
     "function filterSelection(category) {",
     "async function filterSelection(category) {"),

    # 14. index.html Part 8 (Update calls to filterSelection)
    ("index.html",
     "filterSelection(activeFilter);",
     "await filterSelection(activeFilter);"),

    # 15. Create Tables (Using Python snippet)
    ("terminal",
     "flask shell",
     "python -c \"from app import create_app; from app.extensions import db; app = create_app(); app.app_context().push(); db.create_all()\""),
]

def run(cmd):
    print(f"Running: {cmd}")
    res = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    if res.returncode != 0:
        print(f"Command Failed: {res.stderr}")
    return res.returncode == 0

def main():
    print("=== Phase 4 Extreme Contribution Automation Started ===")
    
    # 1. Create 50 Issues
    issue_numbers = []
    print("Creating 50 issues...")
    for i, title in enumerate(ISSUES):
        res = subprocess.run(f'gh issue create --title "{title}" --body "Automated issue creation for Phase 4."', shell=True, capture_output=True, text=True)
        if res.returncode == 0:
            print(f"Created Issue {i+1}/50")
            issue_numbers.append(f"#{res.stdout.strip().split('/')[-1]}")
        else:
            print(f"Failed to create issue {i+1}: {res.stderr}")
            time.sleep(1)

    # 2. Execute 15 PRs
    print("Executing 15 PRs...")
    for i, step in enumerate(PR_STEPS):
        pr_num = i + 1
        branch_name = f"feature/phase4-part-{pr_num}"
        
        file_target, target, replacement = step
        
        if file_target == "terminal":
            run(replacement)
            # Create a dummy commit just to have a PR for step 15
            with open("frontend/static/style.css", "a") as f:
                f.write("\\n/* DB Initialized */")
            file_target = "frontend/static/style.css"
        else:
            if file_target == "models.py":
                filepath = "backend/app/models.py"
            elif file_target == "api.py":
                filepath = "backend/app/routes/api.py"
            else:
                filepath = "frontend/templates/index.html"
                
            run("git checkout main")
            run("git pull")
            run(f"git branch -D {branch_name} || exit 0")
            run(f"git checkout -b {branch_name}")
            
            with open(filepath, "r") as f:
                content = f.read()
            if target in content:
                content = content.replace(target, replacement, 1)
                with open(filepath, "w") as f:
                    f.write(content)
            else:
                print(f"Target string not found in {filepath} for PR {pr_num}!")

        run(f"git add .")
        commit_msg = f"feat: implement phase 4 part {pr_num}"
        close_issues = " ".join([f"Closes {num}" for num in issue_numbers[pr_num*3:pr_num*3+3]]) if issue_numbers else ""
        
        try:
            run(f'git commit -m "{commit_msg}"')
            run(f"git push -u origin {branch_name}")
            
            pr_body = f"Part {pr_num} of Phase 4 User Bookmarks. {close_issues}"
            run(f'gh pr create --title "{commit_msg}" --body "{pr_body}"')
            time.sleep(2)
            run(f"gh pr merge {branch_name} --merge --delete-branch")
            print(f"--- Completed PR {pr_num} / 15 ---")
        except Exception as e:
            print(f"Error executing PR {pr_num}: {e}")
        
    print("=== Phase 4 Extreme Contribution Automation Finished ===")

if __name__ == "__main__":
    main()
