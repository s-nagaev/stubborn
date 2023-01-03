from pygments.styles.solarized import SolarizedDarkStyle
from pygments.token import Keyword, Name, Number


class StubbornDark(SolarizedDarkStyle):
    styles = SolarizedDarkStyle.styles
    styles.update({Number: '#d33682', Name.Tag: '#268bd2', Keyword.Constant: "#cb4b16"})
