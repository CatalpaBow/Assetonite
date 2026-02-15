AssettoCorsaをResoniteでプレイ WIP

### 構造
ReactivePrograming + Layered Architectureもどき

依存関係
Sender:メッセージをシリアライズし、送信する
↑
Message:メッセージソースを元にメッセージを生成する
↑
MessageSource:RawDataからメッセージの生成に必要なデータを生成し、提供
↑
RawData:iniやSharedMemoryといった生のデータを取ってくる

message_server:メッセージングの一連のプロセスをReactiveProgramingで記述
 