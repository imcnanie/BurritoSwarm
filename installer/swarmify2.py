import urwid
from wifi import Cell, Scheme

SSID = [x.ssid for x in Cell.all('wlan0') if "SoloLink" in x.ssid ]
SSID_DICT = {}

for x in SSID:
    SSID_DICT[x] = False
    
def menu(title, SSID):
    body = [urwid.Text(title), urwid.Divider()]
    options = []
    for c in SSID:
        button = urwid.Button("[ ] " + c)
        options.append(button)
        #if SSID_DICT[c] == True:
        #    button.set_label(u"DH")
        urwid.connect_signal(button, 'click', item_chosen, c)
        body.append(urwid.AttrMap(button, None, focus_map='reversed'))

    swarmify_button = urwid.Button("Swarmify")
    options.append(swarmify_button)
    urwid.connect_signal(swarmify_button, 'click', swarm_chosen, c)
    body.append(urwid.AttrMap(swarmify_button, None, focus_map='reversed'))
    
    return urwid.ListBox(urwid.SimpleFocusListWalker(body))

def swarm_chosen(button, choice):
    try:
        copters_chosen = [x+ " \n" for x in SSID_DICT.keys() if SSID_DICT[x] == True]
        response = urwid.Text([u'Swarmifying: \n', copters_chosen, u'\n'])
        done = urwid.Button(u'Ok')
        urwid.connect_signal(done, 'click', exit_program)
        main.original_widget = urwid.Filler(urwid.Pile([response,
                                                        urwid.AttrMap(done, None, focus_map='reversed')]))
    except:
        pass


def item_chosen(button, choice):
    if SSID_DICT[choice]:
        button.set_label(u"[ ] " + button.get_label()[4:])
        SSID_DICT[choice] = False
    else:
        button.set_label(u"[*] " + button.get_label()[4:])
        SSID_DICT[choice] = True
        

    
    ##response = urwid.Text([u'You chose ', str(SSID_DICT[choice]), u'\n'])
    ##done = urwid.Button(u'Ok')


    ##urwid.connect_signal(done, 'click', exit_program)
    ##main.original_widget = urwid.Filler(urwid.Pile([response,
    ##urwid.AttrMap(done, None, focus_map='reversed')]))

def exit_program(button):
    raise urwid.ExitMainLoop()

main = urwid.Padding(menu(u'Choose Solos to Swarmify', SSID), left=2, right=2)
top = urwid.Overlay(main, urwid.SolidFill(u'\N{MEDIUM SHADE}'),
    align='center', width=('relative', 100),
    valign='middle', height=('relative', 100),
    min_width=20, min_height=9)

urwid.MainLoop(top, palette=[('reversed', 'standout', '')]).run()

