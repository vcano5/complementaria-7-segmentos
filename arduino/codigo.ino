const int pines[7] = {2, 3, 4, 6, 5, 7, 8};

const byte nums[11][7] = {
  {0, 0, 0, 0, 0, 0, 0},
  {1, 1, 1, 1, 1, 1, 0}, // 0
  {0, 1, 1, 0, 0, 0, 0}, // 1
  {1, 1, 0, 1, 1, 0, 1}, // 2
  {1, 1, 1, 1, 0, 0, 1}, // 3
  {0, 1, 1, 0, 0, 1, 1}, // 4
  {1, 0, 1, 1, 0, 1, 1}, // 5
  {1, 0, 1, 1, 1, 1, 1}, // 6
  {1, 1, 1, 0, 0, 0, 0}, // 7
  {1, 1, 1, 1, 1, 1, 1}, // 8
  {1, 1, 1, 1, 0, 1, 1}  // 9
};

int contador = 0;
int estadoBoton = HIGH;
int ultimoEstado = HIGH;

void setup() {
  Serial.begin(9600);
  for (int i = 0; i < 7; i++) {
    pinMode(pines[i], OUTPUT);
  }
}

void loop() {
  if(!Serial.available()) return;
  String line = Serial.readStringUntil("\n");
  line.trim();
  if(line.length() == 0) return;
  char cmd = line.charAt(0);
  int num = 0;

  int sp = line.indexOf(' ');
  if(sp == -1) {
    num = line.toInt();
    cmd = 'A';
  }
  else {
    cmd = toupper(line.charAt(0));
    num = line.substring(sp + 1).toInt();
  }

  if(cmd == 'A') {
    mostrarNumero(0);  
  }
  
  else {
    mostrarNumero(num + 1);
  }
  Serial.print("OK ");
  Serial.println(cmd);
}

void mostrarNumero(int numero) {
  for (int i = 0; i < 7; i++) {
    digitalWrite(pines[i], nums[numero][i]);
  }
}