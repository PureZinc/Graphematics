from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.widget import Widget
from kivy.graphics import Line

class DrawingApp(App):
    def build(self):
        # Create the main layout
        layout = BoxLayout(orientation='vertical')

        # Create the drawing area
        self.canvas = DrawingArea()
        layout.add_widget(self.canvas)

        # Create a button to clear the canvas
        clear_button = Button(text='Clear', size_hint_y=None, height=50)
        clear_button.bind(on_press=self.clear_canvas)
        layout.add_widget(clear_button)

        return layout

    def clear_canvas(self, instance):
        self.canvas.clear()

class DrawingArea(Widget):
    def on_touch_down(self, touch):
        with self.canvas:
            touch.ud['line'] = Line(points=(touch.x, touch.y), width=2)

    def on_touch_move(self, touch):
        touch.ud['line'].points += (touch.x, touch.y)

if __name__ == "__main__":
    DrawingApp().run()