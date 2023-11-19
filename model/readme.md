keras.models.load_model("모델 path + 이름") 이용해서 모델 불러와서 사용하면 됩니다. 

테스트 예시:
코드좀 수정했음 흑돌의 경우 1 , 백돌의 경우 2로 그냥 15 * 15 바둑판에 기보 상태 저장했음
shape를 ( 입력 기보 갯수, 15 ,15 1 ) 이런식으로 shape 변환 하면 된다.
 
 board = np.zeros((15, 15), dtype=int)
 board[7,7] = 1
 board[7,8] = 2
 board[6,8] = 1
 board[6,6] = 1
 board = board.reshape(1,15,15,1)
 y_predict = model.predict(board)
