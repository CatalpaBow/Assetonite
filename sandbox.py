'''
msg = 'suspensionMaxTravel,f4,[0.1;0.2;0.3;0.4],carPosOffset,f3,[0.1;0.2;0.3]'
msg = str(msg)
splited_msg = ','.split(msg)
chunk_size = 3
msg_chunks = [splited_msg[i:chunk_size] for i in range(0,len(splited_msg),chunk_size)]
susMax = filter(lambda msg : msg[0] == 'suspensionMaxTravel',msg_chunks)

[print(f'{str}') for str in susMax]
'''

