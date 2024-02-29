# Turk Ai Python Task 

Bu proje, Interpol tarafından yayınlanan kırmızı liste verilerini çeken, bir veritabanına kaydeden ve web üzerinden paylaşan bir uygulamayı içerir.
Detaylı açıklamalar kodların içinde yazılmıştır.


## Başlangıç

Yerel Makinanıza dosyayı çalıştırmak için docker kurmanız gerekecektir.

### Gereksinimler

- Docker ve Docker Compose yüklü olmalıdır.

### Kurulum

1. Bu depoyu yerel makinenize klonlayın.
2. Dosyanın bulunduğu yerde terminalinizi açın.
3. Docker Compose ile projeyi başlatın.(docker-compose up)
4. Web sitesinin oluşturulması 20-25 dk arası sürecektir bunun nedeni veri alma süreci uzun sürmektedir.

### Dipnot
Bazen docker chrome'u kurarken hata verebilmektedir(nadiren olsada) bunun için tekardan başlatmanız gerekmektedir.
1.Terminale docker-compose down yazıp konteynırları silin.
2.docker rmi -f $(docker images -q) komutunu kullanarak var olan eski imageları silmek için bu komutu yazın.
3.Tekrardan docker-compose up komutunu yazıp tekrar kuruluma başlayın.


