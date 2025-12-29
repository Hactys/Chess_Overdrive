from dash import html

files = "abcdefgh"
ranks = list(range(8,0,-1))

def square_id(f,r):
    return f"{f}{r}"

def board_component():
    grid=[]
    for r in ranks:
        row=[]
        for i,f in enumerate(files):
            base_color = "#2c3e50" if (i+r)%2==0 else "#34495e"
            row.append(html.Div(
                id=f"square-{square_id(f,r)}",
                className="board-square",
                style={
                    "width":"60px","height":"60px","display":"flex",
                    "alignItems":"center","justifyContent":"center",
                    "background":base_color,
                    "border":"1px solid #111",
                    "cursor":"pointer","fontSize":"24px",
                    "transition":"0.15s"
                }
            ))
        grid.append(html.Div(row,style={"display":"flex"}))

    return html.Div(grid,id="board",style={
        "display":"inline-block","padding":"5px",
        "border":"4px solid #222","borderRadius":"5px",
        "userSelect":"none"
    })