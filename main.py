import millicord
from millicord.modules import *

token =
millicord.generate_idol_folder('./test_idol', token, [OnMentionedModule, PCallModule, LoggingModule, EchoModule], overwrite=True)
builder = millicord.IdolBuilder.load_from_folder('./test_idol/')
print(builder.modules.modules)
builder.build_and_run()
