import urllib.request, json, sys
sys.path.insert(0, r'C:\Users\ASUS\OneDrive\Desktop\Github_Project\github-copilot-python\starter')
print('Fetching /new')
resp = urllib.request.urlopen('http://127.0.0.1:5000/new?difficulty=easy').read().decode()
data = json.loads(resp)
puzzle = data['puzzle']
print('Puzzle received; solving locally...')
import sudoku_logic
sol = sudoku_logic.solve_sudoku(puzzle)
print('Solved locally? ', sol is not None)
req = urllib.request.Request('http://127.0.0.1:5000/check', data=json.dumps({'board': sol, 'puzzle': puzzle}).encode('utf-8'), headers={'Content-Type':'application/json'})
res = urllib.request.urlopen(req).read().decode()
print('Check response:', res)
