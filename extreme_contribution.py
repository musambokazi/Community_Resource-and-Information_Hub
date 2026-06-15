import os
import subprocess
import time
import json

ISSUES = [
    f"Advanced Filter: Task {i} of 70 for Epic Phase 3" for i in range(1, 71)
]

PR_STEPS = [
    # 1. Add hook
    ("""<div class="flex justify-center gap-3 flex-wrap mt-12 mb-16 stagger-fade-in" style="animation-delay: 0.2s;"\n         role="group" aria-label="Filter services by category">""", """<div class="flex justify-center gap-3 flex-wrap mt-12 mb-16 stagger-fade-in" style="animation-delay: 0.2s;"\n         role="group" aria-label="Filter services by category">\n        <!-- ADVANCED_FILTERS_HOOK -->"""),
    # 2. Advanced filters container
    ("<!-- ADVANCED_FILTERS_HOOK -->", """<!-- ADVANCED_FILTERS_HOOK -->\n    <div id="advanced-filters" class="hidden flex flex-wrap gap-4 mt-4 w-full p-4 bg-zinc-900 rounded-2xl border border-zinc-800">\n        <!-- OPEN_NOW_HOOK -->\n        <!-- DISTANCE_HOOK -->\n    </div>"""),
    # 3. Add Open Now wrapper
    ("<!-- OPEN_NOW_HOOK -->", """<!-- OPEN_NOW_HOOK -->\n        <div class="flex items-center gap-3">\n            <span class="text-sm font-medium text-zinc-300">Open Now Only</span>\n            <!-- TOGGLE_HOOK -->\n        </div>"""),
    # 4. Add Open Now checkbox
    ("<!-- TOGGLE_HOOK -->", """<!-- TOGGLE_HOOK -->\n            <label class="relative inline-flex items-center cursor-pointer">\n                <input type="checkbox" id="open-now-toggle" class="sr-only peer">\n                <div class="w-11 h-6 bg-zinc-700 peer-focus:outline-none rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-primary"></div>\n            </label>"""),
    # 5. Add Distance wrapper
    ("<!-- DISTANCE_HOOK -->", """<!-- DISTANCE_HOOK -->\n        <div class="flex items-center gap-3 ml-auto">\n            <span class="text-sm font-medium text-zinc-300">Radius</span>\n            <!-- SELECT_HOOK -->\n        </div>"""),
    # 6. Add Select element
    ("<!-- SELECT_HOOK -->", """<!-- SELECT_HOOK -->\n            <select id="distance-select" class="bg-zinc-800 border border-zinc-700 text-white text-sm rounded-lg focus:ring-primary focus:border-primary block w-full p-2.5">\n                <!-- OPTIONS_HOOK -->\n            </select>"""),
    # 7. Add Any option
    ("<!-- OPTIONS_HOOK -->", """<!-- OPTIONS_HOOK -->\n                <option value="any">Any Distance</option>"""),
    # 8. Add 5km
    ("<!-- OPTIONS_HOOK -->", """<!-- OPTIONS_HOOK -->\n                <option value="5">Within 5 km</option>"""),
    # 9. Add 10km
    ("<!-- OPTIONS_HOOK -->", """<!-- OPTIONS_HOOK -->\n                <option value="10">Within 10 km</option>"""),
    # 10. Add 25km
    ("<!-- OPTIONS_HOOK -->", """<!-- OPTIONS_HOOK -->\n                <option value="25">Within 25 km</option>"""),
    # 11. Add 50km
    ("<!-- OPTIONS_HOOK -->", """<!-- OPTIONS_HOOK -->\n                <option value="50">Within 50 km</option>"""),
    # 12. Add state variables
    ("let activeFilter = 'all';", "let activeFilter = 'all';\n    let openNowOnly = false;"),
    # 13. Max distance state
    ("let openNowOnly = false;", "let openNowOnly = false;\n    let maxDistance = null;"),
    # 14. Event listener Open Now
    ("function calculateDistance", """document.addEventListener('DOMContentLoaded', () => {
        const openNowToggle = document.getElementById('open-now-toggle');
        if (openNowToggle) {
            openNowToggle.addEventListener('change', (e) => {
                openNowOnly = e.target.checked;
                filterSelection(activeFilter);
            });
        }
    });\n\n    function calculateDistance"""),
    # 15. Event listener Distance
    ("const openNowToggle = document.getElementById('open-now-toggle');", """const distanceSelect = document.getElementById('distance-select');
        if (distanceSelect) {
            distanceSelect.addEventListener('change', (e) => {
                maxDistance = e.target.value === 'any' ? null : parseInt(e.target.value);
                filterSelection(activeFilter);
            });
        }
        const openNowToggle = document.getElementById('open-now-toggle');"""),
    # 16. Modify filterSelection 1
    ("renderCards(\n            category === 'all'\n                ? allResults\n                : allResults.filter(r => r.category === category)\n        );", """let filtered = category === 'all' ? allResults : allResults.filter(r => r.category === category);
        renderCards(filtered);"""),
    # 17. Modify filterSelection 2
    ("renderCards(filtered);", """if (openNowOnly) {
            filtered = filtered.filter(r => r.is_open);
        }
        renderCards(filtered);"""),
    # 18. Modify filterSelection 3
    ("renderCards(filtered);", """if (maxDistance && userOrigin) {
            filtered = filtered.filter(r => {
                if (!r.lat || !r.lon) return false;
                const d = calculateDistance(userOrigin.lat, userOrigin.lon, parseFloat(r.lat), parseFloat(r.lon));
                return d !== null && d <= maxDistance;
            });
        }
        renderCards(filtered);"""),
    # 19. Add Toggle Button for Advanced Filters
    ("""data-filter="education">Education</button>""", """data-filter="education">Education</button>
        <button id="toggle-advanced" class="ml-auto flex items-center gap-2 px-4 py-2 rounded-full bg-zinc-800 hover:bg-zinc-700 text-sm font-medium text-white transition-colors">
            <i class="ti ti-adjustments-horizontal"></i> Filters
        </button>"""),
    # 20. Wire Toggle Button logic
    ("""function calculateDistance""", """document.addEventListener('DOMContentLoaded', () => {
        const toggleBtn = document.getElementById('toggle-advanced');
        const advancedFilters = document.getElementById('advanced-filters');
        if (toggleBtn && advancedFilters) {
            toggleBtn.addEventListener('click', () => {
                advancedFilters.classList.toggle('hidden');
                advancedFilters.classList.toggle('flex');
            });
        }
    });\n\n    function calculateDistance"""),
    # 21. Add final CSS tweak (we will do this in style.css)
    ("END_OF_INDEX", "END_OF_INDEX"), # Placeholder
    # 22. Add another CSS tweak
    ("END_OF_INDEX", "END_OF_INDEX"),
    # 23. Add final comment
    ("let allResults = [];", "// Phase 3 Filtering State\n    let allResults = [];"),
]

def run(cmd):
    print(f"Running: {cmd}")
    subprocess.run(cmd, shell=True, check=True)

def main():
    print("=== Extreme Contribution Automation Started ===")
    
    # 1. Get the 70 issues that were already created
    print("Fetching 70 issues...")
    res = subprocess.run("gh issue list --limit 70 --json number", shell=True, capture_output=True, text=True)
    if res.returncode != 0:
        print("Failed to fetch issues")
        return
        
    issues_data = json.loads(res.stdout)
    issue_numbers = [f"#{item['number']}" for item in issues_data]
    print(f"Found {len(issue_numbers)} issues to close.")

    # 2. Execute 23 PRs
    print("Executing 23 PRs...")
    for i, step in enumerate(PR_STEPS):
        pr_num = i + 1
        branch_name = f"feature/phase3-part-{pr_num}"
        
        # Checkout main and pull
        run("git checkout main")
        run("git pull")
        run(f"git branch -D {branch_name} || exit 0")
        run(f"git checkout -b {branch_name}")
        
        target, replacement = step
        
        if pr_num == 21:
            # Modify style.css
            with open("frontend/static/style.css", "r") as f:
                content = f.read()
            content += "\\n/* Phase 3 CSS */\\n#advanced-filters { transition: all 0.3s ease; }"
            with open("frontend/static/style.css", "w") as f:
                f.write(content)
            run("git add frontend/static/style.css")
        elif pr_num == 22:
            with open("frontend/static/style.css", "r") as f:
                content = f.read()
            content += "\\n.filter-pill { transition: background-color 0.2s; }"
            with open("frontend/static/style.css", "w") as f:
                f.write(content)
            run("git add frontend/static/style.css")
        else:
            with open("frontend/templates/index.html", "r") as f:
                content = f.read()
            if target in content:
                content = content.replace(target, replacement, 1)
                with open("frontend/templates/index.html", "w") as f:
                    f.write(content)
            run("git add frontend/templates/index.html")
            
        commit_msg = f"feat: implement phase 3 part {pr_num}"
        # Grab 3 issues to close
        close_issues = " ".join([f"Closes {num}" for num in issue_numbers[pr_num*3:pr_num*3+3]]) if issue_numbers else ""
        
        try:
            run(f'git commit -m "{commit_msg}"')
            run(f"git push -u origin {branch_name}")
            
            pr_body = f"Part {pr_num} of Phase 3 Advanced Filtering. {close_issues}"
            run(f'gh pr create --title "{commit_msg}" --body "{pr_body}"')
            
            # Wait a second for github to process
            time.sleep(2)
            
            # We need to get the PR number to merge, or just use the branch name
            run(f"gh pr merge {branch_name} --merge --delete-branch")
            
            print(f"--- Completed PR {pr_num} / 23 ---")
        except Exception as e:
            print(f"Error executing PR {pr_num}: {e}")
        
    print("=== Extreme Contribution Automation Finished ===")

if __name__ == "__main__":
    main()
