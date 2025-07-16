import random

# first_name=input('First Name:')
# last_name=input('Last Name:')
# username=input('Username')

def generate_unique_userIDS(username,id_list):
    # name=[first_name,last_name]
    special_chars='$_.~!'

    final=[]
    existing_variates=[]
    for i in range(10):
        
        special_points=[random.choice(special_chars),random.randint(1,500)]
        output_sequence_1=f'{random.choice(special_points)}{username}{random.choice(special_points)}'
        output_sequence_2=f'{username}{random.choice(special_points)}'
        output_sequence_3=f'{random.choice(special_points)}{username}'
        output_sequences=[output_sequence_1,output_sequence_2,output_sequence_3]
        output=random.choice(output_sequences)

    if output not in existing_variates and output not in id_list:
        final.append(output)

    for element in final:
        if element in id_list:
            final.remove(element)
        
    # print(final)
    return final

