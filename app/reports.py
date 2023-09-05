def writeReport(w, resp, h, c, rh):
    j=0
    ws = w.add_worksheet()
    for i in range(len(c)):
        ws.set_column(i,i,c[i])
    hf = w.add_format({'bold': True, 'bg_color': 'green'})
    for i in h:
        ws.write(0, j, i, hf)
        j+=1
    j=1
    for r in resp:
        for i in range(len(h)):
            ws.write(j, i, r[i])
            if rh:
                ws.set_row(j, rh)
        j+=1
