print('gui loaded')
import parse
import draw
import dearpygui.dearpygui as dpg

def button_callback(sender, app_data, user_data):
    print(f"sender is: {sender}")
    print(f"app_data is: {app_data}")
    print(f"user_data is: {user_data}")

    parse.main(user_data['path'])
    draw.main(user_data['output_location'])


def main():

    width, height = 600, 300

    dpg.create_context()
    dpg.create_viewport(title='flowsql', width=width, height=height)

    with dpg.window(label="flowsql", width=width, height=height):
        dpg.add_text(" Welcome to flowsql! \
            \n\n Please specify the desired settings and then hit run :)\n\n")
        in_path = dpg.add_input_text(label="Path", default_value="unit-tests/customers.sql")
        in_outputlocation = dpg.add_input_text(label="Output Location", default_value="outputs")
        btn = dpg.add_button(label="Run")

        dpg.set_item_callback(btn, button_callback)
        dpg.set_item_user_data(btn, {
            'path':dpg.get_value(in_path),
            'output_location':dpg.get_value(in_outputlocation)
        })


    dpg.setup_dearpygui()
    dpg.show_viewport()
    dpg.start_dearpygui()
    dpg.destroy_context()


