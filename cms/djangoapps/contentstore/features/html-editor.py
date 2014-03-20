# disable missing docstring
#pylint: disable=C0111

from lettuce import world, step
from nose.tools import assert_in, assert_equal  # pylint: disable=no-name-in-module
from common import type_in_codemirror, get_codemirror_value

CODEMIRROR_SELECTOR_PREFIX = "$('iframe').contents().find"


@step('I have created a Blank HTML Page$')
def i_created_blank_html_page(step):
    world.create_course_with_unit()
    world.create_component_instance(
        step=step,
        category='html',
        component_type='Text'
    )


@step('I see only the HTML display name setting$')
def i_see_only_the_html_display_name(step):
    world.verify_all_setting_entries([['Display Name', "Text", False]])


@step('I have created an E-text Written in LaTeX$')
def i_created_etext_in_latex(step):
    world.create_course_with_unit()
    step.given('I have enabled latex compiler')
    world.create_component_instance(
        step=step,
        category='html',
        component_type='E-text Written in LaTeX'
    )


@step('I edit the page$')
def i_click_on_edit_icon(step):
    world.edit_component()


@step('I add an image with static link "(.*)" via the Image Plugin Icon$')
def i_click_on_image_plugin_icon(step, path):
    use_plugin(
        '.mce-i-image',
        lambda: world.css_fill('.mce-textbox', path, 0)
    )


@step('I add a link with static link "(.*)" via the Link Plugin Icon$')
def i_click_on_link_plugin_icon(step, path):
    def fill_in_link_fields():
        world.css_fill('.mce-textbox', path, 0)
        world.css_fill('.mce-textbox', 'picture', 1)

    use_plugin('.mce-i-link', fill_in_link_fields)


@step('type "(.*)" in the code editor and press OK$')
def type_in_codemirror_plugin(step, text):
    use_plugin(
        '.mce-i-code',
        lambda: type_in_codemirror(0, text, CODEMIRROR_SELECTOR_PREFIX)
    )


@step('and the code editor displays "(.*)"$')
def verify_code_editor_text(step, text):
    use_plugin(
        '.mce-i-code',
        lambda: assert_equal(text, get_codemirror_value(0, CODEMIRROR_SELECTOR_PREFIX))
    )


def use_plugin(button_class, action):
    # Click on plugin button
    world.css_click(button_class)

    # Wait for the editing window to open.
    world.wait_for_visible('.mce-window')

    # Trigger the action
    action()

    # Click OK
    world.css_click('.mce-primary')


@step('I save the page$')
def i_click_on_save(step):
    world.save_component(step)


@step('the page text is:')
def check_page_text(step):
    assert_equal(step.multiline, world.css_find('.xmodule_HtmlModule').html.strip())


@step('the src link is rewritten to "(.*)"$')
def image_static_link_is_rewritten(step, path):
    # Find the TinyMCE iframe within the main window
    with world.browser.get_iframe('mce_0_ifr') as tinymce:
        image = tinymce.find_by_tag('img').first
        assert_in(path, image['src'])


@step('the href link is rewritten to "(.*)"$')
def link_static_link_is_rewritten(step, path):
    # Find the TinyMCE iframe within the main window
    with world.browser.get_iframe('mce_0_ifr') as tinymce:
        link = tinymce.find_by_tag('a').first
        assert_in(path, link['href'])


@step('the expected toolbar buttons are displayed$')
def check_toolbar_buttons(step):
    dropdowns = world.css_find('.mce-listbox')
    assert_equal(2, len(dropdowns))

    # Format dropdown
    assert_equal('Paragraph', dropdowns[0].text)
    # Font dropdown
    assert_equal('Font Family', dropdowns[1].text)

    buttons = world.css_find('.mce-ico')

    expected_buttons = [
        'bold',
        'italic',
        # This is our custom "code style" button, which uses an image instead of a class.
        'none',
        'underline',
        'forecolor',
        'bullist',
        'numlist',
        'outdent',
        'indent',
        'blockquote',
        'link',
        'unlink',
        'image',
        'code',
    ]

    assert_equal(len(expected_buttons), len(buttons))

    for index, button in enumerate(expected_buttons):
        class_names = buttons[index]._element.get_attribute('class')
        assert_equal("mce-ico mce-i-" + button, class_names)


@step('I set the text to "(.*)" and I select the text$')
def set_text_and_select(step, text):
    script = """
    var editor = tinyMCE.activeEditor;
    editor.setContent(arguments[0]);
    editor.selection.select(editor.dom.select('p')[0]);"""
    world.browser.driver.execute_script(script, str(text))
    world.wait_for_ajax_complete()


@step('I select the code toolbar button$')
def select_code_button(step):
    # This is our custom "code style" button. It uses an image instead of a class.
    world.css_click(".mce-i-none")
