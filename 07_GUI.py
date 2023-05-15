from __future__ import absolute_import
import random
import math
import pyglet
from pyglet import gl
from pyglet.gl import *
from pyglet import shapes
from pyglet.window import mouse
from pyglet.window.key import *
import imgui
from imgui.integrations.pyglet import create_renderer
import math
import pickle
import gensim.downloader as api
import numpy as np
import gensim
import os
from gensim.models.keyedvectors import KeyedVectors

# bert phrase embedding
# algomerative cluster

# CLUSTER: Several clusters result pickle file
# Dict: key - label / value - wordset
CLUSTERS = ["Cluster_results_0.000001_5_00.pickle",
            "Cluster_results_0.000001_6_00.pickle",
            "Cluster_results_0.000001_6_01.pickle",
            "Cluster_results_0.000001_6_02.pickle",
            "Cluster_results_0.000001_6_03.pickle",
            "Cluster_results_0.000001_7_00.pickle",
            "Cluster_results_0.000001_7_01.pickle",
            "Cluster_results_0.000001_7_02.pickle",
            "Cluster_results_0.000001_7_03.pickle",
            "Cluster_results_0.000001_7_04.pickle",
            "Cluster_results_0.000001_8_00.pickle",
            "Cluster_results_0.000001_8_01.pickle",
            "Cluster_results_0.000001_8_02.pickle"]


# RESULT: load CLUSTERS file into a 2d list
RESULT = []
for cluster in CLUSTERS:
    with open(cluster,'rb') as file:
        result = pickle.load(file)
    RESULT.append(result)


# load model(philosophy.kv) as keydVectors wordmap 
# for distance checking
def openModel(modelNameOrFile : str) -> KeyedVectors:
    if os.path.isfile(modelNameOrFile):
        return KeyedVectors.load(modelNameOrFile)
    return gensim.downloader.load(modelNameOrFile)
model = "philosophy.kv"
word_vectors = openModel(model)


# class of a dictionary object 
# attribute dictionary should be the RESULT(2d list of cluster result)
class Worddictionary():
    def __init__(self, dictionary):
        self.dictionary = dictionary
    
    def search(self,search_word,n=4):
        '''
        give a search word
        return a dictionary of four set of its neighbors, each of the set
        is not longer than 30
        key is 01234 / value is a set of words
        '''
        neighbors = {}
        i = 0
        for dicts in self.dictionary:
            for _, word_set in dicts.items():
                if search_word in word_set:
                    if len(word_set) <= 60:
                        neighbors[i] = word_set
                        i += 1
            if i == n:
                break
        # if len(neighbors) < 4:
            # raise TypeError("search another word")
        return neighbors

    def sortneighbors(self,map,search_word):
        '''
        give a neighbors dictionary, the keys are 0123 / values are neighbor words set
        return a sortneighbors which is a dictionary, the key are 0123
        the values are a dictionary which the keys are words /
        values are the distance between the words and the search word
        '''
        neighbors  = self.search(search_word)
        sorted_neighbor = {}
        for k,v in neighbors.items():
            sorted_neighbor[k] = {} 
            for words in v:
                if words != search_word:
                    distance = map.distance(search_word, words)
                    sorted_neighbor[k][words] = distance
        return sorted_neighbor
    
    def calculate_vector(word_a,word_b,word_c):
        '''
        give three words, calculate a - b + c vector sum
        and find the word that is closest to the sum
        '''
        vector_a = word_vectors[word_a]
        vector_b = word_vectors[word_b]
        vector_c = word_vectors[word_c]
        vector_sum = vector_a + vector_b - vector_c
        similar = word_vectors.similar_by_vector(vector_sum,2)[1][0]
        sim_vector = word_vectors[similar]

        return similar, sim_vector



# create a instance of worddictionary
DICTS = Worddictionary(RESULT)

# GUI and pyglet visulization
class AppWindow(pyglet.window.Window):
    def __init__(self, *args, **kwargs):
        # setup
        super().__init__(*args, **kwargs)
        self.windowwidth = args[0]
        self.windowheight = args[1]
        self.radius = self.windowheight/2 - 20

        self.set_minimum_size(400,300)
        gl.glClearColor(200, 200, 200, 200)
        imgui.create_context()
        self.imguiImpl = create_renderer(self)
        self.push_handlers(pyglet.window.event.WindowEventLogger())
        self.set_icon(pyglet.image.load('logo.png'))

        self.neighbors = None

        # operation attribute setup
        self.labels = None
        self.search_word = None
        self.last_search = None
        self.click_list_word = None
        self.last_pow = None
        self.distance_label = None
        self.cal_a = None
        self.cal_b = None
        self.cal_c = None
        self.operation = None
        self.count = 0
        self.simword = None
        self.simdistance = None
        # batch for all background static shapes
        self.batch = pyglet.graphics.Batch()
        center = (self.windowwidth/2, self.windowheight/2)
        self.background = shapes.Rectangle(0, 0, self.windowwidth, self.windowheight, color=(10, 10, 10, 255), batch=self.batch)
        self.circle1 = shapes.Circle(center[0], center[1], 100, color=(90, 90, 90,50), batch=self.batch)
        self.circle2 = shapes.Circle(center[0], center[1], 200, color=(90, 90, 90,50), batch=self.batch)
        self.circle3 = shapes.Circle(center[0], center[1], 330, color=(90, 90, 90,50), batch=self.batch)
        self.circle4 = shapes.Circle(center[0], center[1], 500, color=(90, 90, 90,50), batch=self.batch)


        self.timer = 0.0
        self.result = set()

        
    # IMGUI
    def updateUI(self):
        imgui.new_frame()
        if imgui.begin_main_menu_bar():
            if imgui.begin_menu("Menu", True):
                clicked_quit, selected_quit = imgui.menu_item(
                    "Quit", 'Cmd+Q', False, True
                )
                if clicked_quit:
                    exit(1)
 
                imgui.end_menu()
            imgui.end_main_menu_bar()
 
        imgui.begin("search the word", True)
        imgui.set_window_position(20,40)
        imgui.text("search something about philosophy here")
        if self.search_word is None:
            last_search_word = ""
        else:
            
            last_search_word = self.search_word
        changed,last_search_word= imgui.input_text("searchword", last_search_word,100,32)
        # imgui.text("Hello")
        
        if self.last_pow is None or changed == True or self.last_search != self.search_word:
            self.pow_slider_value = 10
        else:
            self.pow_slider_value = self.last_pow
        self.slider_change, self.pow_slider_value = imgui.slider_int("pow int", self.pow_slider_value, 0, 20)
        self.last_pow = self.pow_slider_value
        self.pow_value = self.pow_slider_value * 0.1
        imgui.text("distance pow: {}".format(self.pow_value))

        # if imgui.button("search"):
        #     # print("Pressed")
        #     self.star.color = (255, 0, 0)
        #     imgui.open_popup("popup")
        
 
        if self.result != set():
            imgui.text(str(self.result))
        imgui.end()
        
        self.neighborwindowposition = [(20,220),(1380,40),(20,700),(1380,700)]
        
        if self.neighbors != None:
            for k,v in self.neighbors.items():
                imgui.begin("cluster{} -  amount of words:{}".format(k,len(v)))
                imgui.set_window_position(self.neighborwindowposition[k][0],self.neighborwindowposition[k][1])
                imgui.set_window_size(300,320)
                for word in v:
                    if imgui.button(word):
                        self.click_list_word = word
                        self.check_click()
                imgui.end()
        
        self.caluculate_window()

        if changed == True:
            return last_search_word
        
    # def check_button_click(self,button):
    #     if button:
    #         return button.label
    def caluculate_window(self):
        imgui.begin("calculation")
        imgui.set_window_position(330,40)
        imgui.set_window_size(300,100)
        imgui.text("word1:{} + word2:{} - word3:{}".format(self.cal_a,self.cal_b,self.cal_c))
        imgui.text("result:{}{}".format(self.simword,self.simdistance))
        cal_bool = imgui.button("Calculate!")
        if self.cal_a != None and self.cal_b != None and self.cal_c != None and cal_bool == True:
            self.simword, self.simvector = Worddictionary.calculate_vector(self.cal_a,self.cal_b,self.cal_c)
            self.simdistance = word_vectors.distance(self.search_word,self.simword)

        imgui.end()

    def drawScene(self):
        self.timer += 0.1
        self.batch.draw()
    # @self.event
    def on_draw(self):
        self.clear()

        self.drawScene()
        
        # get the search word input form imgui
        k = self.updateUI()
        if k is not None:
            self.search_word = k

        # if is searching for a new word
        # fund its neighbors in 4 different cluster reuslt
        # create labels and points instance for them
        if self.search_word != None and self.last_search != self.search_word:
            self.circle1.radius = 100
            self.circle2.radius = 170
            self.circle3.radius = 300
            self.neighbors  = self.search_function(self.search_word)
            self.label_circle =  self.create_label(self.neighbors)[1]
            self.labels = self.create_label(self.neighbors)[0]
            self.simdistance = None
            
        if self.slider_change:
            self.label_circle =  self.create_label(self.neighbors, self.pow_value)[1]
            self.labels = self.create_label(self.neighbors, self.pow_value)[0]
            self.circle1.radius = 100 * (2-self.pow_value)
            self.circle2.radius = 170 * (2-self.pow_value)
            self.circle3.radius = 300 * (2-self.pow_value)
        # iterate all instances of labels and points to draw them
        if self.labels != None:
            for label in self.labels:
                label.draw()
            for circles in self.label_circle:
                circles.draw()
        if self.simdistance != None : 
            angle = 4
            distance_norm = normalize(self.simdistance,self.d_min,self.d_max)
            pos_y = math.pow(distance_norm,self.pow_value) * self.radius * math.sin(angle) + 0.5 * self.windowheight
            pos_x = math.pow(distance_norm,self.pow_value) * self.radius * math.cos(angle) + 0.5 * self.windowwidth
            self.sim_label = pyglet.text.Label(self.simword,
                          font_name='Times New Roman',
                          font_size=15,
                          x=pos_x, y=pos_y)
            self.sim_circle = pyglet.shapes.Circle(pos_x,pos_y,5,color=(255,255,255))
            self.sim_circle.draw()
            self.sim_label.draw()
            
        # if self.distance_label != None:
        #     for distance_labels in self.distance_label:
        #         distance_labels.draw()
        self.last_search = self.search_word
        imgui.render()
        
        self.imguiImpl.render(imgui.get_draw_data())

    def on_key_press(self, symbol, modifiers):
        if symbol == pyglet.window.key.ESCAPE:
            self.close()

    def on_mouse_drag(self, x, y, dx, dy, buttons, modifiers):
        pass

    def on_mouse_scroll(self, x, y, scroll_x, scroll_y):
        pass
    

    def on_mouse_press(self, x, y, button, modifiers):
        self.cursor = (x,y)
        # if mouse is pressed, check if the user is clicking a point
        if self.labels != None:
            self.check_overlapping(self.cursor)
        

    def on_close(self):
        self.imguiImpl.shutdown()
        imgui.destroy_context()
        super().on_close()

    def search_function(self,search_word):
        '''
        search a word in DICTS, return a dictionary of dictionary
        return:
             {0:{'word1':0.66,'word2':0.65},1:{'word3':0.66,'word4':0.65}...}
        '''
        # print(search_word)
        # print("resutl",DICTS.sortneighbors(word_vectors,search_word))
        return DICTS.sortneighbors(word_vectors,search_word)

    
    def create_label(self,neighbors,pow_value=1.0):
        '''
        given a dictionary of dictionary neighbors, return shape instances
        args: {0:{'word1':0.66,'word2':0.65},1:{'word3':0.66,'word4':0.65}...}
        Return: the instances of labels and points
        '''

        leftup = neighbors[0]
        rightup = neighbors[1]
        leftdown = neighbors[2]
        rightdown = neighbors[3]
        labels = []
        circles = []
        self.d_min = np.min(list(leftup.values())+list(rightup.values())+list(leftdown.values())+list(rightdown.values()))
        self.d_max = np.max(list(leftup.values())+list(rightup.values())+list(leftdown.values())+list(rightdown.values()))
        angle = 0.25
        j = 0.25
        for word,distance in rightup.items():
            distance_norm = normalize(distance,self.d_min,self.d_max)
            pos_y = math.pow(distance_norm,pow_value) * self.radius * math.sin(angle) + 0.5 * self.windowheight
            pos_x = math.pow(distance_norm,pow_value) * self.radius * math.cos(angle) + 0.5 * self.windowwidth
            if pow_value ==1:
                font_sizes =10
            elif pow_value > 1:
                font_sizes = math.pow(distance_norm,pow_value) * 8 + 8
            else:
                font_sizes = abs(1-math.pow(distance_norm,pow_value)) * 8 + 8
            label = pyglet.text.Label(text=word,
                                      font_size=font_sizes, 
                                      color= (10, 255, 255, 255),
                                      x = pos_x, y = pos_y)
            distance_label = pyglet.text.Label(text=str(distance),
                                      font_size=font_sizes*0.7,
                                      color= (200, 100, 100, 0),
                                      x = pos_x, y = pos_y)
            if distance == self.d_max:
                horizon_label = pyglet.text.Label(text="horizon: {}".format(distance),
                                                    font_name='Times New Roman',
                                                    font_size=font_sizes*0.7,
                                                    color= (200, 200, 200, 255),
                                                    x = pos_x+10, y = pos_y-10)
                labels.append(horizon_label)
                horizon_box = shapes.Star(pos_x-10, pos_y-10, 10, 5,6, color=(255, 0, 0,100))
                circles.append(horizon_box)
            circle = shapes.Circle(pos_x, pos_y, 5, color=(50, 225, 30))
            labels.append(label)
            labels.append(distance_label)
            circles.append(circle)
            if (angle > 0.5*math.pi - 0.25) or (angle<0.25):
                j = -j
            angle += j 
        angle = 0.5*math.pi + 0.25
        j = 0.25
        for word,distance in leftup.items():
            distance_norm = normalize(distance,self.d_min,self.d_max)
            pos_y = math.pow(distance_norm,pow_value) * self.radius * math.sin(angle) + 0.5 * self.windowheight
            pos_x = math.pow(distance_norm,pow_value) * self.radius * math.cos(angle) + 0.5 * self.windowwidth
            if pow_value ==1:
                font_sizes =10
            elif pow_value > 1:
                font_sizes = math.pow(distance_norm,pow_value) * 8 + 8
            else:
                font_sizes = abs(1-math.pow(distance_norm,pow_value)) * 8 + 8
            label = pyglet.text.Label(text=word,
                                      font_size=font_sizes,
                                      color= (100, 200, 255, 255),
                                      x = pos_x, y = pos_y)
            distance_label = pyglet.text.Label(text=str(distance),
                                      font_size=font_sizes*0.7,
                                      color= (200, 100, 100, 0),
                                      x = pos_x, y = pos_y)
            if distance == self.d_max:
                horizon_label = pyglet.text.Label(text="horizon: {}".format(distance),
                                                    font_name='Times New Roman',
                                                    font_size=font_sizes*0.7,
                                                    color= (200, 200, 200, 255),
                                                    x = pos_x+10, y = pos_y-10)
                labels.append(horizon_label)
                horizon_box = shapes.Star(pos_x-10, pos_y-10, 10, 5, 6, color=(255, 0, 0 ,100))
                circles.append(horizon_box)
            circle = shapes.Circle(pos_x, pos_y, 5, color=(100, 60, 30))
            labels.append(label)
            labels.append(distance_label)
            circles.append(circle)
            if (angle > math.pi - 0.25) or (angle < 0.5*math.pi + 0.25):
                j = -j
            angle += j 
            # print(angle)
        angle = math.pi + 0.26
        j = 0.25
        for word,distance in leftdown.items():
            distance_norm = normalize(distance,self.d_min,self.d_max)
            pos_y = math.pow(distance_norm,pow_value) * self.radius * math.sin(angle) + 0.5 * self.windowheight
            pos_x = math.pow(distance_norm,pow_value) * self.radius * math.cos(angle) + 0.5 * self.windowwidth
            if pow_value ==1:
                font_sizes =10
            elif pow_value > 1:
                font_sizes = math.pow(distance_norm,pow_value) * 8 + 8
            else:
                font_sizes = abs(1-math.pow(distance_norm,pow_value)) * 8 + 8
            label = pyglet.text.Label(text=word,
                                      font_size=font_sizes,
                                      color= (200, 100, 100, 255),
                                      x = pos_x, y = pos_y)
            distance_label = pyglet.text.Label(text=str(distance),
                                      font_size=font_sizes*0.7,
                                      color= (200, 100, 100, 0),
                                      x = pos_x, y = pos_y)
            if distance == self.d_max:
                horizon_label = pyglet.text.Label(text="horizon: {}".format(distance),
                                                    font_name='Times New Roman',
                                                    font_size=font_sizes*0.7,
                                                    color= (200, 200, 200, 255),
                                                    x = pos_x+10, y = pos_y-10)
                horizon_box = shapes.Star(pos_x-10, pos_y-10, 10, 5, 6, color=(255, 0, 0,100))
                circles.append(horizon_box)
                labels.append(horizon_label)
            circle = shapes.Circle(pos_x, pos_y, 5, color=(90, 30, 100))
            labels.append(label)
            labels.append(distance_label)
            circles.append(circle)
            if (angle > 1.5* math.pi - 0.25) or (angle < math.pi + 0.25):
                j = -j
            angle += j 
            # print(angle)
        angle = 1.5 * math.pi + 0.26
        j = 0.25
        for word,distance in rightdown.items():
            distance_norm = normalize(distance,self.d_min,self.d_max)
            pos_y = math.pow(distance_norm,pow_value) * self.radius * math.sin(angle) + 0.5 * self.windowheight
            pos_x = math.pow(distance_norm,pow_value) * self.radius * math.cos(angle) + 0.5 * self.windowwidth
            if pow_value ==1:
                font_sizes =10
            elif pow_value > 1:
                font_sizes = math.pow(distance_norm,pow_value) * 8 + 8
            else:
                font_sizes = abs(1-math.pow(distance_norm,pow_value)) * 8 + 8
            label = pyglet.text.Label(text=word,
                                      font_size=font_sizes,
                                      color= (150, 200, 100, 255),
                                      x = pos_x, y = pos_y)
            distance_label = pyglet.text.Label(text=str(distance),
                                      font_size=font_sizes*0.7,
                                      color= (200, 100, 100, 0),
                                      x = pos_x, y = pos_y)
            if distance == self.d_max:
                horizon_label = pyglet.text.Label(text="horizon: {}".format(distance),
                                                    font_name='Times New Roman',
                                                    font_size=font_sizes*0.7,
                                                    color= (200, 200, 200, 255),
                                                    x = pos_x+10, y = pos_y-10)
                horizon_box = shapes.Star(pos_x-10, pos_y-10, 10, 5, 6, color=(255, 0, 0,100))
                labels.append(horizon_label)
                circles.append(horizon_box)
            circle = shapes.Circle(pos_x, pos_y, 5, color=(20, 30, 120))
            labels.append(label)
            labels.append(distance_label)
            circles.append(circle)
            if (angle > 2* math.pi - 0.25) or (angle < 1.5*math.pi + 0.25):
                j = -j
            angle += j 

        
        return labels,circles
    
    def check_overlapping(self,cursor):
        '''
        check if the cursor is clicking a word point
        if so, set that word as next search word
        '''
        for circle in self.label_circle:
            if abs(cursor[0] - circle.x) < 5 and abs(cursor[1]-circle.y) < 5:
                circle.color = (0, 0, 0, 255)
        for labels in self.labels:
            if abs(cursor[0] - labels.x) < 5 and abs(cursor[1]-labels.y) < 5 and "." not in labels.text:
                self.search_word = labels.text
                # print("check_over",self.search_word)
        if self.sim_label != None:
            if abs(cursor[0]- self.sim_label.x) < 5 and abs(cursor[1]-self.sim_label.y) < 5:
                self.search_word = self.sim_label.text
                # print("check_over",self.search_word)
    
    def check_click(self):
        '''
        check the button that user click, and turn the button word name circle 
        into another color
        '''
        randomcolor = (random.randint(100,255), random.randint(100,255), random.randint(100,255), 255)
        for labels in self.labels:
            if labels.text == self.click_list_word:
                if self.count%3 == 0:
                    self.cal_a = labels.text
                elif self.count%3 == 1:
                    self.cal_b = labels.text
                else:
                    self.cal_c = labels.text
                self.count+=1
                the_pos = (labels.x,labels.y)
                labels.color = randomcolor
                labels.font_size = 20
                for labels in self.labels:
                    if labels.x == the_pos[0] and labels.y == the_pos[1] and labels.text != self.click_list_word:
                        labels.color = (200,200,200,255)
                        labels.y = labels.y -10
                        labels.x = labels.x +5


def normalize(datas,d_min,d_max,MIN=0.01,MAX=1):
    return (datas - d_min) / (d_max - d_min) * (MAX - MIN) + MIN
        
if __name__ == "__main__":
    
    window = AppWindow(1720,1060,"Kluster - Mining to the Edge",resizable = False)
    # window.resizeable = True
    # width=1280, height=720,resizable=True
    # check = worddictionary(RESULT)
    # search_w = window.on_draw()
    pyglet.app.run()
    # while True:
    #     print("do")
    #     if search_w != None:
    #         print(check.search(search_w))
    
    # print(check.search("follow"))
    
               # pos_y = math.pow(distance+0.1,0.8) * 250 * math.sin(angle) + 360
            # pos_x = math.pow(distance+0.1,0.8) * 250 * math.cos(angle) + 640
            # pos_y = math.pow((distance * 250 * math.sin(angle) + 360),1.01)
            # pos_x = math.pow(distance * 250 * math.cos(angle) + 640,1.01)
            # pos_y = (distance)**1.3 * 250 * math.sin(angle) + 360
            # pos_x = (distance)**1.3 * 250 * math.cos(angle) + 640