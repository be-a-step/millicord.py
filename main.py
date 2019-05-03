import millicord

token =
millicord.generate_idol_folder('./test_idol', token, [], overwrite=True)
builder = millicord.IdolBuilder.load_from_folder('./test_idol/')
builder.build_and_run()
