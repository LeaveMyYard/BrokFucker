import React, { useEffect, useState } from "react";
import { useParams } from "react-router-dom";
import lotsService from "../services/Lots";
import dateFix from "../utils/dateFix";
import translateService from "../services/Translate";

export default function LotHistoryPage() {
  const [loading, setLoading] = useState(true);
  const [lot, setLot] = useState();
  let { id } = useParams();

  const refreshList = async () => {
    setLoading(true);

    try {
      const lot = await lotsService.getLotHistory(id);
      setLot(lot);
    } catch (error) {
      setLot();
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    refreshList();
  }, []);

  return loading ? (
    <h1 className="lot-history_heading">Loading...</h1>
  ) : (
    <div className="lot-history_container">
      {lot.map((lot, lotIndex) => (
        <div key={lot.id}>
          <h3>
            {lotIndex + 1}. {lot.name}
          </h3>
          <p>
            <img width="200" src={lot.user_avatar} alt="avatar"></img>
          </p>
          <p>
            {lot.confirmed
              ? "Лот подтверждён"
              : "Лот находится на рассмотрении"}
          </p>
          <p>Пользователь: {lot.user_display_name}</p>
          <p>Email: {lot.user}</p>
          <p>Дата публикации: {dateFix(lot.date)}</p>
          <p>Дата подтверждения: {dateFix(lot.approve_date)}</p>
          <p>Комментарий: {lot.commentary}</p>
          <p>Сумма: {lot.amount}</p>
          <p>Валюта: {lot.currency}</p>
          <p>Срок, мес: {lot.term}</p>
          <p>Метод погашения: {translateService(lot.return_way)}</p>
          <p>Обеспечение: {lot.security}</p>
          <p>Ставка годовых: {lot.percentage}</p>
          <p>Форма кредитирования: {translateService(lot.form)}</p>
          <p>Проверенное обеспечение: {lot.security_checked ? "Да" : "Нет"}</p>
          <p>Гарантия клуба: {lot.guarantee_percentage}</p>
          {lot.club_guarantee_requested && lot.verification_requested ? (
            <p>Заказаны: Гарантия клуба и проверенное обеспечение</p>
          ) : lot.club_guarantee_requested && !lot.verification_requested ? (
            <p>Заказаны: Гарантия клуба</p>
          ) : !lot.club_guarantee_requested && lot.verification_requested ? (
            <p>Заказаны: Проверенное обеспечение</p>
          ) : (
            <p>Заказаны: ничего</p>
          )}
          <div>
            <p>Фото:</p>
            {lot.photos.photos.map((photo, photoIndex) => (
              <img
                key={photoIndex}
                width="250"
                src={photo}
                alt="lot_photo"
              ></img>
            ))}
          </div>
        </div>
      ))}
    </div>
  );
}
