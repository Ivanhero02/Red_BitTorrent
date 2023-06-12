import libtorrent as lt
import time
import datetime
import threading

def torrent_download(link):
    # Configuración de la sesión y parámetros de descarga
    ses = lt.session()
    ses.listen_on(6881, 6891)
    params = {
        'save_path': '/Descargas',
    }
    print(link)

    # Agregar el enlace magnet a la sesión
    handle = lt.add_magnet_uri(ses, link, params)
    ses.start_dht()

    begin = time.time()
    print(datetime.datetime.now())

    print('Descargando Metadata...')
    while not handle.has_metadata():
        time.sleep(1)
    print('Metadata Obtenida, Iniciando descarga...')

    print("Starting", handle.name())

    # Bloque para pausar y reanudar la descarga
    paused = False
    def input_thread(L):
        nonlocal paused
        while True:
            a = input()
            if a.lower() == 'pause':
                paused = True
            elif a.lower() == 'resume':
                paused = False
            else:
                print("Comandos válidos son 'pause' y 'resume'")

    L = []
    thread = threading.Thread(target=input_thread, args=(L,))
    thread.daemon = True
    thread.start()

    # Monitoreo de la descarga
    while handle.status().state != lt.torrent_status.seeding:
        if paused:
            print("Descarga pausada...")
            while paused:
                time.sleep(1)
        else:
            s = handle.status()
            state_str = ['en cola', 'checando', 'descargando metadata', \
                    'descargando', 'finalizado', 'seeding', 'allocating']
            print('%.2f%% complete (down: %.1f kb/s up: %.1f kB/s peers: %d) %s ' % \
                    (s.progress * 100, s.download_rate / 1000, s.upload_rate / 1000, \
                    s.num_peers, state_str[s.state]))
        time.sleep(5)

    end = time.time()
    print(handle.name(), "Descarga Completa")

    print("Tiempo demorado: ", int((end - begin) // 60), "min :", int((end - begin) % 60), "sec")
    print(datetime.datetime.now())

def create_torrent_file(file_path, tracker):
    # Crear archivo torrent a partir de un archivo local
    fs = lt.file_storage()
    lt.add_files(fs, file_path)

    creator = lt.create_torrent(fs)
    creator.add_tracker(tracker)
    creator.set_creator('My Torrent Creator')

    torrent_path = file_path + ".torrent"

    with open(torrent_path, "wb") as f:
        f.write(lt.bencode(creator.generate()))

    print("Torrent file created:", torrent_path)

def generate_magnet(torrent_file):
    # Generar enlace magnet a partir de un archivo torrent
    info = lt.torrent_info(torrent_file)
    link = f'magnet:?xt=urn:btih:{info.info_hash()}&dn={info.name()}'
    for tracker in info.trackers():
        link += f'&tr={tracker.url}'
    return link

def download_thread(link):
    # Función auxiliar para iniciar la descarga en un hilo separado
    t = threading.Thread(target=torrent_download, args=(link,))
    t.start()

while True:
    choice = input("¿Deseas cargar o descargar? (cargar/descargar/salir): ")
    if choice.lower() == 'salir':
        break
    elif choice.lower() == 'cargar':
        file_path = input("Seleccione la ubicación del archivo de descarga: ")
        tracker = input("Seleccione el tracker a utilizar: ")
        create_torrent_file(file_path, tracker)
        torrent_file = file_path + ".torrent"
        magnet_link = generate_magnet(torrent_file)
        print("Magnet link:", magnet_link)
    elif choice.lower() == 'descargar':
        num_downloads = int(input("¿Cuántas descargas simultáneas deseas realizar? "))
        for _ in range(num_downloads):
            link = input("Escribe tu enlace magnet/torrent: ")
            download_thread(link)
    else:
        print("Opción no válida. Por favor, elige 'cargar', 'descargar' o 'salir'.")