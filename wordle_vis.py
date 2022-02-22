# -*- coding: utf-8 -*-
"""
Created on Tue Feb 22 20:59:58 2022

@author: tobycrisford
"""

def create_vis(words, colours, file_out):
    
    lines = ["<html>","<body>",'<svg viewBox="0 0 ' + str(len(words[0]) * 200) + ' ' + str(len(words) * 200) + '" xmlns="http://www.w3.org/2000/svg">']
    for i in range(len(words)):
        for j in range(len(words[i])):
            rect_line = '<rect x="' + str(j * 100 + 10) + '" y="' + str(i * 100 + 10) + '" width="80" height="80" style="fill:'
            if colours[i][j] == "*":
                rect_line += "green"
            elif colours[i][j] == ".":
                rect_line += "orange"
            else:
                rect_line += "grey"
            rect_line += '"/>'
            lines.append(rect_line)
            lines.append('<text x="' + str(j * 100 + 50) + '" y="' + str(i * 100 + 50) + '" text-anchor="middle" stroke="white" stroke-width="1px", fill="white" font-family="Arial">')
            lines.append(words[i][j].upper())
            lines.append('</text>')
    lines.append("</svg></body></html>")
    
    with open(file_out, "w") as f:
        f.writelines([line + "\n" for line in lines])
    