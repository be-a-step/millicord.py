import millicord
from millicord.modules import *

token = 'replace this string to valid token'
idol = millicord.generate_idol_folder('./test_idol',
                                      token,
                                      [LoggingModule,
                                       PCallModule,
                                       TimeKeepingModule,
                                       RandomResposeModule],
                                      overwrite=True)
idol.run(token)
