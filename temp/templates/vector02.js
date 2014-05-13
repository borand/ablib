///////////////////////////////////////////
// Global variables
var active_tab;
var debug_websocket = false;
var debug_js = true;
var debug_all = true;

////////////////////////////////////////
// Chart and plot variables
var plot_height = 700;
var chart;
var plot;
var power = -5;
var constl_plot_1;
var constl_plot_2;

////////////////////////////////////////
// 3D Surface Plot
var cnst = [[0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],[0,0,0,0,1,1,1,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,2,0,2,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,2,0,0,0],[0,0,0,11,9,12,8,3,1,0,0,0,0,0,0,0,0,0,0,0,0,2,10,12,8,7,2,0,0,0,0,0,0,0,0,0,0,0,0,1,13,5,9,5,5,0,0,0,0,0,0,0,0,0,0,0,0,2,7,11,9,4,1,0],[0,0,3,21,42,63,31,18,3,0,0,0,0,0,0,0,0,0,0,0,4,9,37,51,53,10,2,0,0,0,0,0,0,0,0,0,0,0,4,10,24,66,55,17,8,1,0,0,0,0,0,0,0,0,0,0,0,3,31,63,73,30,9,0],[0,0,7,52,148,174,117,41,3,2,0,0,0,0,0,0,0,0,0,0,5,41,110,179,153,62,13,1,0,0,0,0,0,0,0,0,0,0,4,21,97,152,176,46,25,0,0,0,0,0,0,0,0,0,0,0,2,14,62,159,170,91,33,0],[1,0,8,78,181,235,166,49,6,0,0,0,0,0,0,0,0,0,0,0,9,50,123,235,209,65,10,0,0,0,0,0,0,0,0,0,0,0,1,34,113,255,201,100,18,4,0,0,0,0,0,0,0,0,0,0,0,20,88,210,220,132,30,5],[0,1,4,46,118,131,105,28,8,0,0,0,0,0,0,0,0,0,0,1,7,26,108,156,121,53,7,0,0,0,0,0,0,0,0,0,0,0,3,27,79,142,154,54,13,1,1,0,0,0,0,0,0,0,0,0,0,12,52,127,164,85,20,3],[0,0,3,14,37,49,39,8,1,0,0,0,0,0,0,0,0,0,0,1,4,4,30,43,33,15,3,0,0,0,0,0,0,0,0,0,0,0,0,4,32,43,50,12,3,0,0,0,0,0,0,0,0,0,0,0,0,3,14,49,44,27,6,2],[0,0,1,2,3,9,5,1,0,0,0,0,0,0,0,0,0,0,1,0,0,2,4,12,3,2,0,0,0,0,0,0,0,0,0,0,0,0,0,1,2,6,5,3,1,0,0,0,0,0,0,0,0,0,0,0,0,0,6,6,7,4,0,0],[0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,1,0,0],[0,0,0,3,3,4,3,1,1,0,0,0,0,0,0,0,0,0,0,0,0,1,5,8,6,0,1,0,0,0,0,0,0,0,0,0,0,0,1,2,2,5,4,2,1,0,0,0,0,0,0,0,0,0,0,0,0,0,1,3,4,5,0,0],[0,0,3,11,28,49,26,6,0,0,0,0,0,0,0,0,0,0,0,0,0,7,29,45,31,12,2,1,0,0,0,0,0,0,0,0,0,0,2,3,29,59,46,19,5,2,0,0,0,0,0,0,0,0,0,0,0,4,14,41,51,22,2,1],[0,0,10,41,128,168,93,42,4,0,0,0,0,0,0,0,0,0,0,1,7,28,105,160,116,37,14,0,0,0,0,0,0,0,0,0,0,0,1,22,70,133,126,70,10,1,0,0,0,0,0,0,0,0,0,0,2,9,71,126,151,73,12,0],[0,0,10,57,157,232,132,66,10,1,0,0,0,0,0,0,0,0,0,1,7,53,137,226,196,67,14,1,0,0,0,0,0,0,0,0,0,0,3,30,126,218,212,95,22,3,0,0,0,0,0,0,0,0,0,0,3,23,96,215,228,141,32,1],[0,2,9,59,153,176,113,52,3,2,0,0,0,0,0,0,0,0,0,1,3,37,114,193,147,57,10,1,0,0,0,0,0,0,0,0,0,0,5,20,105,145,167,83,17,1,1,0,0,0,0,0,0,0,0,0,0,15,72,149,152,88,23,2],[0,1,5,24,55,74,45,14,1,0,0,0,0,0,0,0,0,0,0,0,6,17,47,63,38,14,4,0,0,0,0,0,0,0,0,0,0,0,2,6,33,71,56,34,5,1,0,0,0,0,0,0,0,0,0,0,0,7,31,62,73,32,15,2],[0,0,2,1,10,12,5,2,0,0,0,0,0,0,0,0,0,0,0,0,0,2,7,15,10,2,1,0,0,0,0,0,0,0,0,0,0,0,0,1,4,13,10,6,0,0,0,0,0,0,0,0,0,0,0,0,1,0,7,13,14,10,3,0],[0,0,0,0,1,0,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,0,0,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,2,2,2,0,0],[0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],[0,0,0,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],[0,0,1,2,2,3,0,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,4,3,0,0,0,0,0,0,0,0,0,0,0,0,0,0,2,0,5,2,1,1,0,0,0,0,0,0,0,0,0,0,0,0,2,1,3,1,1,0,0],[0,0,1,17,23,23,22,4,0,0,0,0,0,0,0,0,0,0,0,0,1,10,14,30,24,9,4,1,0,0,0,0,0,0,0,0,0,0,1,5,13,26,28,7,2,1,0,0,0,0,0,0,0,0,0,0,0,2,15,34,34,20,6,1],[0,1,6,33,84,133,83,23,4,0,0,0,0,0,0,0,0,0,0,0,3,18,72,116,95,42,4,1,0,0,0,0,0,0,0,0,0,0,1,15,61,129,90,65,12,2,0,0,0,0,0,0,0,0,0,0,1,6,45,113,108,57,22,4],[0,2,15,62,188,210,158,40,5,0,0,0,0,0,0,0,0,0,0,1,5,43,127,254,186,71,17,1,0,0,0,0,0,0,0,0,0,0,4,33,105,221,204,101,17,2,0,0,0,0,0,0,0,0,0,0,2,17,67,217,227,115,29,3],[0,1,14,56,160,196,149,45,6,0,0,0,0,0,0,0,0,0,0,0,8,37,107,193,153,70,15,0,0,0,0,0,0,0,0,0,0,0,5,26,99,216,161,73,20,3,0,0,0,0,0,0,0,0,0,0,1,15,82,188,209,123,26,6],[0,0,3,32,69,92,53,23,2,1,0,0,0,0,0,0,0,0,0,0,3,14,61,82,76,33,9,0,0,0,0,0,0,0,0,0,0,0,2,8,45,93,95,35,7,1,0,0,0,0,0,0,0,0,0,0,1,5,31,63,71,57,11,3],[0,0,2,4,15,25,12,2,0,0,0,0,0,0,0,0,0,0,0,0,0,4,24,29,24,5,1,0,0,0,0,0,0,0,0,0,0,0,0,4,9,11,22,9,1,0,0,0,0,0,0,0,0,0,0,0,0,2,10,22,18,8,3,0],[0,0,0,0,1,3,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,1,1,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,2,2,4,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,4,1,0,0,0],[0,0,0,0,0,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,0,0,0],[0,0,0,0,2,3,1,2,0,0,0,0,0,0,0,0,0,0,0,0,0,1,5,2,0,1,1,0,0,0,0,0,0,0,0,0,0,0,0,0,1,0,1,3,0,0,0,0,0,0,0,0,0,0,0,0,0,1,1,1,1,0,0,0],[0,0,1,9,17,15,6,2,0,0,0,0,0,0,0,0,0,0,0,0,1,6,17,19,14,4,0,0,0,0,0,0,0,0,0,0,0,0,0,1,9,24,18,6,1,0,0,0,0,0,0,0,0,0,0,0,0,2,5,18,25,15,3,1],[0,0,3,24,52,109,69,22,3,0,0,0,0,0,0,0,0,0,0,2,3,15,77,111,77,26,2,1,0,0,0,0,0,0,0,0,0,0,1,13,28,71,89,44,7,0,1,0,0,0,0,0,0,0,0,0,1,8,39,73,87,36,12,4],[0,0,11,54,160,219,129,32,9,0,0,0,0,0,0,0,0,0,0,0,5,39,129,193,152,64,14,0,0,0,0,0,0,0,0,0,0,0,4,23,107,190,190,84,15,2,0,0,0,0,0,0,0,0,0,0,1,10,81,158,206,99,30,5],[0,0,19,58,165,246,149,41,7,0,0,0,0,0,0,0,0,0,0,1,14,40,133,212,174,98,9,1,1,0,0,0,0,0,0,0,0,1,2,33,118,228,214,92,11,2,0,0,0,0,0,0,0,0,0,0,1,21,96,195,203,128,29,4],[0,3,5,28,84,122,95,31,1,0,0,0,0,0,0,0,0,0,0,0,3,22,69,122,87,36,5,1,0,0,0,0,0,0,0,0,0,0,1,12,67,119,110,55,12,2,0,0,0,0,0,0,0,0,0,0,2,8,51,107,133,69,13,4],[0,0,2,8,22,42,19,3,0,0,0,0,0,0,0,0,0,0,0,0,3,9,18,26,22,6,1,0,0,0,0,0,0,0,0,0,0,0,0,4,17,18,36,10,4,0,1,0,0,0,0,0,0,0,0,0,0,4,9,32,35,21,4,2],[0,0,0,0,2,5,2,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,4,5,6,1,0,0,0,0,0,0,0,0,0,0,0,0,1,1,0,2,3,1,2,0,0,0,0,0,0,0,0,0,0,0,0,0,2,5,4,3,1,0]];
var SurfacePlot;
var surface_plot_1;
var surface_plot_2;

var surface_size = 64;
var surface_plot_options;
var surface_plot_matrix;
var surface_plot_matrix_1;
var surface_plot_matrix_2;

var accum_matrix_1 = new Array(64);
var accum_matrix_2 = new Array(64);


var tooltipStrings = new Array();

var constl;

///////////////////////////////////////////
// UTILITY FUNCTIONS
//
//
function dbg(message) {
	console.log(message);
	show_server_msg(message);
}
function show_server_msg(message) {
	if (debug_all)
	{	
		$("#debug_console").html( $("#debug_console").text() + message + '\n');					
	    var psconsole = $('#debug_console');
	    psconsole.scrollTop(psconsole[0].scrollHeight - psconsole.height());
	}
}
function set_object_value(id, val){
	var datarole = $("#"+id).attr('data-role');
	dbg('id:' + id + " data-role: " + datarole + "  val: " + val);
	switch(datarole){
		case 'slider':
			dbg('case: slider');
			$('#' + id).val(val).slider("refresh");
			break;
		case 'flipswitch':			
			dbg('about to flip the switch value to:' + val + ' currently set to: ' + $('#' + id).val());
			$('#' + id).val(val).flipswitch("refresh");
			break;
		case 'text':
			$('#' + id).text(val);
			break
		default:
			dbg('case: default');
			$('#' + id).val(val)[datarole]("refresh");
	}
}
function SendCmd(cmd, val) {
	return $.getJSON('/cmd/', "cmd=" + cmd + "&param=" + val, function(data) {			
		$("#cmd_status").text(data.cmd);
	});
}
///////////////////////////////////////////////////////////////////////
// 3D Surface Plot

google.load("visualization", "1");

function init_surface_plot_variables(num_of_cols){
	matrix    = new google.visualization.DataTable();	
	for (var i = 0; i < num_of_cols; i++) {
		matrix.addColumn('number', 'col' + i);
	}
	matrix.addRows(num_of_cols);
	return matrix;
}
function init_surface_plot_options(){

	// Don't fill polygons in IE. It's too slow.
	var fillPly = true;

	// Define a colour gradient.
	var colour1 = {
		red : 0,
		green : 0,
		//blue : 0
		blue : 255
	};
	var colour2 = {
		red : 0,
		green : 255,
		blue : 255
	};
	var colour3 = {
		red : 0,
		green : 255,
		blue : 0
	};
	var colour4 = {
		red : 255,
		green : 255,
		blue : 0
	};
	var colour5 = {
		red : 255,
		green : 0,
		blue : 0
	};
	var colours = [colour1, colour2, colour3, colour4, colour5];

	// Axis labels.
	var xAxisHeader = "I";
	var yAxisHeader = "Q";
	var zAxisHeader = "Z";

	var options = {
		xPos : 0,
		yPos : 0,
		width : 500,
		height : 500,
		colourGradient : colours,
		fillPolygons : fillPly,
		tooltips: tooltipStrings,
		xTitle : xAxisHeader,
		yTitle : yAxisHeader,
		zTitle : zAxisHeader,
		restrictXRotation : true
	};
	return options;
}
function reset_constl(matrix){
	for (var i = 0; i < surface_size; i++) {
		for (var j = 0; j < surface_size; j++) {
			matrix[i][j] = 0;
		}
	}
	return matrix;
}
function add_to_constl(matrix, matrixB){
	for (var i = 0; i < surface_size; i++) {
		for (var j = 0; j < surface_size; j++) {
			matrix[i][j] += matrixB[i][j];
		}
	}
	return matrix;
}
function reset_surface_plot(SurfacePlot, surface_plot_matrix) {		
	
	var idx = 0;	
	for (var i = 0; i < surface_size; i++) {
		for (var j = 0; j < surface_size; j++) {			
			surface_plot_matrix.setValue(i, j, 0);
			tooltipStrings[idx] = "I:" + i + ", Q:" + j + " = 0";
			idx++;
		}
	}
	SurfacePlot.draw(surface_plot_matrix, surface_plot_options);
}
function draw_surface_plot(SurfacePlot, surface_matrix,accum_matrix,cnst) {	
	var idx = 0;	
	var value_norm = 0;
	var value_new = 0;
	var value_max = 1;
	var NORM = 0.3;
	
	// increment the values in surface_plot_matrix(which stores the values) and find the maximum values
	for (var i = 0; i < surface_size; i++) {
		for (var q = 0; q < surface_size; q++) {
			if (accum_matrix[i] == null){
				// initialize the array if required
				accum_matrix[i] = new Array(surface_size);
			}
			
			if (accum_matrix[i][q] == null)
				accum_matrix[i][q] = cnst[i][q];
			else if (cnst[i][q] != 0) {
				accum_matrix[i][q] += cnst[i][q];
				
				if (accum_matrix[i][q] > value_max){
					// track the maximum value
					value_max = accum_matrix[i][q];
				}
			}
		}
	}
	
	// iterate through all of the values, normalizing to the peak value
	
	// initialize storage for each row of x values	
	for (var i = 0; i < surface_size; i++) {
		for (var q = 0; q < surface_size; q++) {
			if (cnst[i][q] != 0) {
				value_new = accum_matrix[i][q] / value_max;
				value_norm = value_new * NORM;
				surface_matrix.setValue(i,q,value_norm);
				
				tooltipStrings[idx] = "I:" + i + ", Q:" + q + " = " + value_new;
				idx++;
			}
		}
	}
//	error('test')
	
	SurfacePlot.draw(surface_matrix, surface_plot_options);
}
///////////////////////////////////////////////////////////////////////
// HIGHCHARTS
//
//

function draw_chart(render_to) {
	
	Highcharts.setOptions({
		global : {
			useUTC : false
		}
	});
	
	// Create the chart
	chart = new Highcharts.StockChart({
		chart : {
			renderTo : render_to,
			height : plot_height,			
		},
		
		rangeSelector: {
			buttons: [{
				count: 1,
				type: 'minute',
				text: '1M'
			}, {
				count: 5,
				type: 'minute',
				text: '5M'
			}, {
				type: 'all',
				text: 'All'
			}],
			inputEnabled: false,
			selected: 0
		},		
		title : {
			text : 'BER 1sec'
		},
		
		exporting: {
			enabled: false
		},
		
		legend : {
			enabled: true
		},
		
		yAxis : {
			title : {
				text : 'BER'
			},
			max : 0.034,
			min : 0.005,
		},
		
		series : [{
			name : 'Flex 3',
			color: '#00FF00',
			step: true,
			data : (function() {
				// generate an array of random data
				var data = [], time = (new Date()).getTime(), i;

				for( i = -99; i <= 0; i++) {
					data.push([
						time + i * 1000,
						0.0
					]);
				}
				return data;
			})()
		},
		{
			name : 'NL Compensated',
			color: '#FF00FF',
			step: true,
			data : (function() {
				// generate an array of random data
				var data = [], time = (new Date()).getTime(), i;

				for( i = -200; i <= 0; i++) {
					data.push([
						time + i * 1000,
						0.0
					]);
				}
				return data;
			})()
		}]
	});
	return chart;
}

function draw_constl_plot(render_to) {
	plot2 = new Highcharts.Chart({
		chart : {
			renderTo : render_to,
			defaultSeriesType : 'scatter',
			zoomType : 'xy',
			height : plot_height,			
		},
		title : {
			text : ''
		},
		subtitle : {
			text : ''
		},
		xAxis : {
			title : {
				enabled : true,
				text : 'I'
			},
			//startOnTick : true,
			//endOnTick : true,
			showLastLabel : true,
			min : -250,
			max : 250,
		},
		yAxis : {
			title : {
				text : 'Q'
			},
			min : -250,
			max : 250,			
		},		
		plotOptions : {
			scatter : {
				marker : {
					radius : 4,					
				},
			}
		},
		series : [{
			name : 'X-POL',
			color : 'rgba(255, 0, 0, .5)',
			//data : [[75, 75],[75, 150], [150, 75],[150, 150]],
			data : [[0,0]],
		},{
			name : 'Y-POL',
			color : 'rgba(0, 0, 255, .5)',
			//data : [[75, 75],[75, 150], [150, 75],[150, 150]],
			data : [[0,0]],

		}]
	});
	return plot2;
}

function draw_plot(render_to) {
	plot = new Highcharts.Chart({
		chart : {
			renderTo : render_to,
			defaultSeriesType : 'spline',
			zoomType : 'xy',
			height : plot_height,			
		},
		title : {
			text : '10 Span TrueWave Classic Link'
		},
				
		xAxis : {
			title : {
				//enabled : true,
				text : 'Launch Power [dBm]'
			},
			startOnTick : true,
			endOnTick : true,
			//showLastLabel : true
		},
		yAxis : {
			title : {
				text : 'OSNR [dB]'
			},
			min : 18,
			max : 30,			
		},		
		series : [{
			name : 'OSNR',
			color : 'rgba(223, 83, 83, .5)',
			data : [[-7.227642228,18.78005522],[-6.493160923,19.60441204],[-5.840186774,20.23582122],[-5.264737174,20.83486006],[-4.713271089,21.35456673],[-4.18455946,21.86171387],[-3.6673595,22.32129401],[-3.159096758,22.80259139],[-2.656017984,23.24259485],[-2.153269216,23.69902273],[-1.653861978,24.11686369],[-1.137068274,24.59787169],[-0.6267458141,25.0371591],[-0.1084156952,25.49336029],[0.3994961276,25.9214208],[0.9203468169,26.34521812],[1.424615485,26.75987359],[1.921136365,27.1473685],[2.41083256,27.51166033],[2.90704792,27.89087585],[3.399259585,28.24317057]],

		},{
			name : 'Current Launch Power',			
			// data : [[power, 0],[power, 6]]
			data : [[power, 18],[power, 34]]
		}]
	});
	return plot;
}

function add_measurement(value){
	var t = (new Date()).getTime();
	for (i=0;i<value.length;i++){
		series = chart.series[i];
		series.addPoint([t, value[i]], true, true);	
	}
}

function update_const_plot(plot_id, data) {	
	dbg('update_const_plot(' + plot_id + ")");
	switch(plot_id) {
		case 'constl_plot_1': {
			dbg('   case: constl_plot_1');
			constl_plot_1.series[0].update({ data : data});			
			break;
		}
		case 'constl_plot_2': {
			constl_plot_2.series[0].update({ data : data});
			break;
		}
		default:
		break
		
	}
}

function rotate_const_plot(angle) {
	surface_plot_1.surfacePlot.currentZAngle = angle[0];
	surface_plot_1.surfacePlot.currentXAngle = angle[1];
	surface_plot_1.surfacePlot.render();

	surface_plot_2.surfacePlot.currentZAngle = angle[0];
	surface_plot_2.surfacePlot.currentXAngle = angle[1];
	surface_plot_2.surfacePlot.render();
}


function parse_message(message_text){
	var temp;
}
///////////////////////////////////////////////////////////////////////
// WEBSOCKETS FUNCTIONS
//
//
function open_websocket(hostname, hostport, hosturl) {

	dbg('Attempting to open web socket');
	function show_message(message) {
		show_server_msg(message);		
	}

	var websocket_address = "ws://" + hostname + ":" + hostport + "/" + hosturl;
	var ws = new WebSocket(websocket_address);
	
	ws.onopen = function() {
		dbg('web socket open');
		$('#live').text('CONNECTED');
		$("#live").css("background-color",'#B2BB1E');
	};

	ws.onmessage = function(event) {
		//dbg('incomming message');
		var JsonData;
		try {
			JsonData = JSON.parse(event.data);			
			if (JsonData.hasOwnProperty('id')) {
				//console.log(JsonData.id);
				switch(JsonData.id)
				{	
					case 'chart':{
						add_measurement(JsonData.val);
						break;
					}
					case 'const':{						
						//update_const_plot(JsonData.val.id, JsonData.val.data);						
						//draw_surface_plot(JsonData.val.data);
						plotid = JsonData.val.id;
						cnst   = JsonData.val.data;
						//console.log(plotid);
						if(plotid == 1){
							draw_surface_plot(surface_plot_1, surface_plot_matrix_1,accum_matrix_1, cnst);	
						} else {
							draw_surface_plot(surface_plot_2, surface_plot_matrix_2,accum_matrix_2, cnst);	
						}
						break;
					}
					case 'launch_power':{
						power = JsonData.val;
						plot.series[1].update({ data : [[power, 18],[power, 34]]});
						break;
					}					
					case 'accum':{	
						pdate_const_plot(JsonData.val.id, JsonData.val.data);						
						break;
					}
					default:{	
						set_object_value(JsonData.id,JsonData.val);
					}
				}
				
			}
			else if(JsonData.hasOwnProperty('data')){
				add_measurement(JsonData.data);
			}
			else{
				add_measurement(JsonData);
			}

		} catch(e) {
			dbg('JSON.parse error: "' + e + '". JsonData = ' + JsonData);			
		}
		//show_server_msg(event.data);
	};
	ws.onclose = function() {
		dbg('closing websockets');
		$('#live').text('OFFLINE');
		$("#live").css("background-color",'#C71C2C');
	};
}

function connect_to_websocket_host(){
	var hostname = $('#hostname').val();
	var hostport = $('#hostport').val();
	var hosturl  = $('#hosturl').val();
	dbg('Pressed button: button_connect: [host, port] ' + hostname +':' + hostport + '/'+ hosturl);
	open_websocket(hostname, hostport, hosturl);
}
///////////////////////////////////////////////////////////////////////
// MAIN GUI - jQUERY
//
//
$(document).ready(function() {	
	
	$("#underline").append("<img id='underline' src='static/line.jpg'/>");
	//$("#page_header").css("background-color",'#C71C2C');
	$("#surf_plot_group1").css("background-color",'#FFFFFF');
	$("#surf_plot_group2").css("background-color",'#FFFFFF');

	dbg('Document ready');

	debug_websocket = $('#debug_websocket').prop("checked");
	debug_js        = $('#debug_js').prop("checked");
	debug_all       = $('#debug_all').prop("checked");
	
	$( "#radio-websocket-online" ).prop( "checked", false ).checkboxradio( "refresh" );	
	$('#debug_console').attr('style', 'background-color:White; font-size:14px; height: 20em;');
	$('#debug_console').textinput("option", "autogrow", false);
	$("#live").css("background-color",'#C71C2C');
	
	$('#button_power_up').hide();
	$('#button_power_down').hide();

	// Draw Highchart Data
	chart        = draw_chart('chart');
	plot         = draw_plot('power_plot');
	//constl_plot_1 = draw_constl_plot('constl_plot_1');
	//constl_plot_2 = draw_constl_plot('constl_plot_2');

	surface_plot_1 = new greg.ross.visualisation.SurfacePlot(document.getElementById('constl_plot_1'));
	surface_plot_2 = new greg.ross.visualisation.SurfacePlot(document.getElementById('constl_plot_2'));
	
	surface_plot_matrix_1 = init_surface_plot_variables(surface_size);
	surface_plot_matrix_2 = init_surface_plot_variables(surface_size);
	surface_plot_options  = init_surface_plot_options();
	
	cnst = reset_constl(cnst);
	draw_surface_plot(surface_plot_1, surface_plot_matrix_1,accum_matrix_1, cnst);
	cnst = reset_constl(cnst);
	draw_surface_plot(surface_plot_2, surface_plot_matrix_2,accum_matrix_2, cnst);
	//reset_surface_plot(surface_plot_1, surface_plot_matrix_1);
	//reset_surface_plot(surface_plot_2, surface_plot_matrix_2);
	//reset_surface_plot(SurfacePlot[0], surface_plot_matrix[0]);
	
	connect_to_websocket_host();
	
	///////////////////////////////////////////////////////////////////////				
	$.getJSON('/cmd/', "cmd=get_power", function(data) {
		console_response_msg(data.res);
	});
	
	///////////////////////////////////////////////////////////////////////
	//
	// BUTTONS
	//

	$("#button_connect").click(function() {	
		connect_to_websocket_host();
	});

	$("#button_clear_debug_console").click(function() {
		$("#debug_console").text("");
	});

	$("#button_power_up").click(function() {		
		if ($('#power_control_enabled').prop("checked")) {
			dbg("button_power_up");
			cmd = 'power_up';
			$.getJSON('/cmd/', "cmd=" + cmd, function(data) {
				console_response_msg(data.res);
			});
			reset_surface_plot(surface_plot_1, surface_plot_matrix_1);
			reset_surface_plot(surface_plot_2, surface_plot_matrix_2);
		}
		else{
			dbg("Power control disabled");
		}
		});
	
	$("#button_power_down").click(function() {		
		if ($('#power_control_enabled').prop("checked")) {
			dbg("button_power_down");
			cmd = 'power_down';			
			$.getJSON('/cmd/', "cmd=" + cmd, function(data) {
				console_response_msg(data.res);
			});
			reset_surface_plot(surface_plot_1, surface_plot_matrix_1);
			reset_surface_plot(surface_plot_2, surface_plot_matrix_2);
		}
		else{
			dbg("Power control disabled");
		}
		});

		$("#power_control_enabled").click(function(){
		if ($('#power_control_enabled').prop("checked")) {
			$('#button_power_up').show();
			$('#button_power_down').show();
		} else {
			$('#button_power_up').hide();
			$('#button_power_down').hide();
		}
	});

	$("#const_rotate_xy").click(function(){
		rotate_const_plot([0,0]);    	
	});
	$("#const_rotate_xz").click(function(){
		rotate_const_plot([0,90]);    	
	});
	$("#const_rotate_default").click(function(){
		rotate_const_plot([45,45]);    	
	});

	
	$("#constellation_tab_button").click(function(){
		dbg('constellation_tab_button clicked');
		reset_surface_plot(surface_plot_1, surface_plot_matrix_1);
		reset_surface_plot(surface_plot_2, surface_plot_matrix_2);
	});

	//TODO - determine which tab is active
	 // $("a.tabs").click(function(event){
  //       var item = $("a.tabs").text();
  //       if (active_tab !== item) {
  //               console.log(item + ": now active");
  //               active_tab = item;
  //       } else {
  //           console.log(item + ": do nothing");            
  //       }
  //       active_tab = item;
  //   });

});
